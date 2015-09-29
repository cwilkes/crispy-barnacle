from app import db

import datetime
from sqlalchemy.ext.declarative import declarative_base
import os


Base = declarative_base()


class IdMixin(object):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)


class InsertTimeMixin(object):
    inserted = db.Column(db.DateTime, default=datetime.datetime.now)


class Project(Base, IdMixin, InsertTimeMixin):
    __tablename__ = 'projects'
    short_name = db.Column(db.Text, nullable=False, primary_key=True)
    long_name = db.Column(db.Text, nullable=True)
    logo = db.Column(db.Text, nullable=True)

    def __init__(self, short_name, long_name=None, logo=None):
        self.short_name, self.long_name, self.logo = short_name, long_name, logo


class XmlUploads(Base, IdMixin, InsertTimeMixin):
    __tablename__ = 'xml_uploads'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    filename = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    url = db.Column(db.Text, nullable=True)

    def __init__(self, project_id, filename, date, url=None):
        self.project_id, self.filename = project_id, filename
        self.date, self.url = date, url


class ClashesJson(Base, IdMixin, InsertTimeMixin):
    __tablename__ = 'clashes_json'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    xml_upload_id = db.Column(db.Integer, db.ForeignKey('xml_uploads.id'), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    data = db.Column(db.Text, nullable=False)

    def __init__(self, project_id, date, data, xml_upload_id=None):
        self.project_id, self.date = project_id, date
        self.data, self.xml_upload_id = data, xml_upload_id


class ClashesCombinedJson(Base, IdMixin, InsertTimeMixin):
    __tablename__ = 'clashes_combined_json'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    data = db.Column(db.Text, nullable=False)

    def __init__(self, project_id, data):
        self.project_id, self.data = project_id, data
