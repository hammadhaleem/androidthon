from app import db
import flask.ext.whooshalchemy

# set the location for the whoosh index


class shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), index=True, unique=True)


class faq(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000), index=True, unique=True)
    answer = db.Column(db.String(1000), index=True, unique=True)
    keywords = db.Column(db.String(1000))

    def __unicode__(self):
        return (self.question)


class path(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    x1 = db.Column(db.Integer)
    y1 = db.Column(db.Integer)

    def __init__(self, x, y, x1, y1):
        self.x = x
        self.y = y
        self.x1 = x1
        self.y1 = y1

    def __unicode__(self):
        return self.id


class rack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rack_name = db.Column(db.String(1000), index=True)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    x1 = db.Column(db.Integer)
    y1 = db.Column(db.Integer)
    prods = db.relationship('product', backref='Rack', lazy='dynamic')

    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        selfname = name
        self.x1 = int(x) + 20
        self.y1 = int(y) - 65

    def __unicode__(self):
        return 'Rack %r' % (self.id)


class product(db.Model):
    __searchable__ = ['name', 'tags']  # these fields will be indexed by whoosh

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), index=True, unique=True)
    tags = db.Column(db.String(1000))
    rack_id = db.Column(db.Integer, db.ForeignKey('rack.id'))
    shelf = db.Column(db.Integer)

    def __init__(self, name, rack_id, shelf, tags):
        self.name = name
        self.rack_id = rack_id
        self.shelf = shelf
        self.tags = tags

    def __unicode__(self):
        return 'Product %r' % (self.name)
