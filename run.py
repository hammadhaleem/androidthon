#!flask/bin/python
from app import app
from flask.ext.admin import Admin
from flask import g
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin import expose
from app.models import *
import flask.ext.whooshalchemy as whooshalchemy


class FedoraModelView(sqla.ModelView):
    column_display_pk = True
    column_display_pk = True

app.config['WHOOSH_BASE'] = ''
whooshalchemy.whoosh_index(app, product)
admin = Admin(app)


admin.add_view(FedoraModelView(path, db.session))
admin.add_view(FedoraModelView(faq, db.session))
admin.add_view(FedoraModelView(product, db.session))
admin.add_view(FedoraModelView(rack, db.session))

app.run(debug=True, host='0.0.0.0')
