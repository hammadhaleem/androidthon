from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
rack = Table('rack', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('rack_name', String(length=1000)),
    Column('x', Integer),
    Column('y', Integer),
    Column('x1', Integer),
    Column('y1', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['rack'].columns['x1'].create()
    post_meta.tables['rack'].columns['y1'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['rack'].columns['x1'].drop()
    post_meta.tables['rack'].columns['y1'].drop()
