from flask import render_template, flash, jsonify
from app import app
from flask.ext.admin import Admin
from flask import g
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin import expose
from app.models import *


def distance(x, y, k, m):
    data = ((x - k) ** 2) + ((y - m) ** 2)
    if data > 0:
        return data
    else:
        return -1 * int(data)


@app.route('/')
@app.route('/rack/<x>/<y>/<name>/')
@app.route('/rack/<x>/<y>/<name>')
def index(x=None, y=None, name=None):
    if x is None or y is None or name is None:
        return jsonify(
            status='Error')
    else:
        mini = 9999
        min_x = 999
        min_y = 9999
        r = rack(x, y, name)
        db.session.add(r)
        query = path.query.all()

        for pa in query:
            dist1 = distance(pa.x, pa.y, r.x1, r.y1)
            if dist1 < mini:
                min_x = pa.x1
                min_y = pa.y1
                mini = dist1
            dist2 = distance(pa.x, pa.y, r.x1, r.y1)
            if dist2 < mini:
                min_x = pa.x1
                min_y = pa.y1
                mini = dist2

        p = path(r.x1, r.y1, min_x, min_y)
        db.session.add(p)
        db.session.commit()
        return jsonify(
            status='Added')


@app.route('/path/<x>/<y>/<x1>/<y1>/')
@app.route('/path/<x>/<y>/<x1>/<y1>')
def index1(x=None, y=None, x1=None, y1=None):
    if x is None or y is None or x1 is None or y1 is None:
        return jsonify(
            status='Error')
    else:
        r = path(x, y, x1, y1)
        db.session.add(r)
        db.session.commit()
        return jsonify(
            status='Added')


@app.route('/obj/<name>/<rad_id>/<shelf>/')
@app.route('/obj/<name>/<rad_id>/<shelf>/')
@app.route('/obj/<name>/<rad_id>/<shelf>/<tags>')
@app.route('/obj/<name>/<rad_id>/<shelf>/<tags>/')
def index2(name=None, rad_id=None, shelf=None, tags=None):
    if name is None or rad_id is None or shelf is None:
        return jsonify(
            status='Error')
    else:
        r = product(name, rad_id, shelf, tags)
        db.session.add(r)
        db.session.commit()
        return jsonify(
            status='Added')


def bfs(graph, start, end):
    # maintain a queue of paths
    queue = []
    # push the first path into the queue
    queue.append([start])
    while queue:
        # get the first path from the queue
        path = queue.pop(0)
        # get the last node from the path
        node = path[-1]
        # path found
        if node == end:
            return path
        # enumerate all adjacent nodes, construct a new path and push it into
        # the queue
        for adjacent in graph.get(node, []):
            new_path = list(path)
            new_path.append(adjacent)
            queue.append(new_path)


@app.route('/search/<data>/')
@app.route('/search/<data>')
def search(data=None):
    lis = []
    if data is None:
        return jsonify(data=[])
    else:

        result = product.query.whoosh_search(data).all()
        for i in result:
            dic = {
                'name': i.name,
                'rack': i.rack_id,
                'shelf': i.shelf
            }
            lis.append(dic)
        return jsonify(data=lis)


@app.route('/tags/')
@app.route('/tags/')
@app.route('/tags/<data>')
@app.route('/tags/<data>/')
def tags(data=None):
    if data is None:
        result = product.query.all()
    else:
        result = product.query.whoosh_search(data).all()
    tags = []
    for i in result:
        dummy = i.tags.split(',')
        for j in dummy:
            tags.append(str(j))
        tags.append(str(i.name))
    return jsonify(tags=tags)


@app.route('/data/')
@app.route('/data')
@app.route('/data/<st>/<en>/')
@app.route('/data/<st>/<en>')
def gets(st=None, en=None):

    rac = []
    query = rack.query.all()
    for q in query:
        rac.append(str(q.x1) + ',' + str(q.y1))

    lis = []
    query = path.query.all()
    for q in query:

        lis.append([str(q.x) + ',' + str(q.y), str(q.x1) + ',' + str(q.y1)])
    dic = {}

    for i in lis:
        try:
            dic[i[0]].append(i[1])
        except:
            dic[i[0]] = []
            dic[i[0]].append(i[1])

        try:
            dic[i[1]].append(i[0])
        except:
            dic[i[1]] = []
            dic[i[1]].append(i[0])

    if st is None or en is None:
        return jsonify(dic)
    else:
        pa = bfs(dic, st, en)
        return jsonify(path=pa, rack=rac)
