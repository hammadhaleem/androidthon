from flask import render_template, flash, jsonify, url_for
from app import app
from flask.ext.admin import Admin
from flask import g
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin import expose
from app.models import *

import math

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from random import randint


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/')
def main():
    u1 = url_for('static', filename='js/jquery-2.1.0.min.js')
    u2 = url_for('static', filename='js/kinetic-v5.0.2.min.js')
    u3 = url_for('static', filename='js/grid.png')
    u4 = url_for('static', filename='img/Guidage.png')
    return render_template('index.html', u1=u1, u2=u2, u3=u3, u4=u4)


def distance(x, y, k, m):
    x = int(x)
    y = int(y)
    k = int(k)
    m = int(m)
    data = ((x - k) ** 2) + ((y - m) ** 2)
    if data > 0:
        return math.sqrt(data)
    else:
        return math.sqrt(-1 * int(data))


@app.route('/racks/')
@app.route('/racks')
@crossdomain(origin='*')
def all_racks():
    lis = []
    query = rack.query.all()
    for data in query:
        lis.append({
            'x': data.x,
            'y': data.y,
            'name': data.rack_name

        })
    return jsonify(items=lis)


@app.route('/rack/<x>/<y>/<name>/')
@app.route('/rack/<x>/<y>/<name>')
def index(x=None, y=None, name=None):
    if x is None or y is None or name is None:
        return jsonify(
            status='Error')
    else:
        mini = 9999999999999999999999999999999999999999999999999
        min_x = -9999
        min_y = -9999
        r = rack(x, y, name)
        query = path.query.all()
        for pa in query:

            dist1 = distance(pa.x, pa.y, r.x1, r.y1)
            dist2 = distance(pa.x1, pa.y1, r.x1, r.y1)

            if dist1 <= mini:
                min_x = int(pa.x)
                min_y = int(pa.y)
                mini = dist1

            print dist1, dist2, mini, min_x, min_y

            if dist2 <= mini:
                min_x = int(pa.x1)
                min_y = int(pa.y1)
                mini = dist2

            print dist1, dist2, mini, min_x, min_y

        p = path(r.x1, r.y1, min_x, min_y)

        db.session.add(p)
        db.session.add(r)
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
@crossdomain(origin='*')
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
@crossdomain(origin='*')
def search(data=None):
    lis = []
    if data is None:
        return jsonify(data=[])
    else:

        result = product.query.whoosh_search(data).all()
        for i in result:
            rac = rack.query.filter_by(id=i.rack_id).first()
            dic = {
                'name': i.name,
                'rack': i.rack_id,
                'shelf': i.shelf
            }
            try:
                dic['x'] = rac.x1
                dic['y'] = rac.y1
            except:
                pass
            lis.append(dic)
        return jsonify(data=lis)


@app.route('/tags/')
@app.route('/tags/')
@app.route('/tags/<data>')
@app.route('/tags/<data>/')
@crossdomain(origin='*')
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


@app.route('/data')
@app.route('/data/')
@app.route('/data/<st>/<en>')
@app.route('/data/<st>/<en>/')
@crossdomain(origin='*')
def gets(st=None, en=None):

    rac = []
    lis = []
    query = rack.query.all()
    for q in query:
        rac.append(str(q.x1) + ',' + str(q.y1))

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
        try:
            d = dic[st]
            d = dic[en]
        except:
            resp = jsonify(path=[], rack=[])
            return resp
        pa = bfs(dic, st, en)
        if not pa:
            pa = []

        offer = {
            0: '50% off in Shoes',
            1: '25% off on men shampoo',
            2: '15% off on sugar',
            3: '15% off on fruits',
            4: '30% off on stationary.',
            5: '23% off on printers',
            6: '23% off on drinks',
            7: '12% off on soaps',
            8: '12% off on shirts',
        }
        prom = {}
        executed_offers = []
        for i in pa:
            if i in rac:
                prom[i] = {}
                for j in xrange(0, 2):
                    ran = randint(0, 8)
                    if ran not in executed_offers:
                        executed_offers.append(ran)
                        try:
                            prom[i].append(offer[ran])
                        except:
                            prom[i] = []
                            prom[i].append(offer[ran])
        resp = jsonify(path=pa, rack=rac, promotion=prom)
        return resp
