from sqlalchemy import create_engine
import falcon
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import settings
import json
from datetime import date, datetime
from sqlalchemy import Integer, ForeignKey, String, Column, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, joinedload, Load, with_polymorphic
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import ModelSchema

# pip install gunicorn on mac, currently using waitress on windows

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

db_engine = create_engine(
    '{engine}://{username}:{password}@{host}:{port}/{db_name}'.format(
    **settings.POSTGRESQL
    )
)

Session = scoped_session(sessionmaker(bind=db_engine))

class SQLAlchemySessionManager:
    """
    Create a scoped session for every request and close it when the request
    ends.
    """

    def __init__(self, Session):
        self.Session = Session

    def process_resource(self, req, resp, resource, params):
        resource.session = self.Session()

    def process_response(self, req, resp, resource, req_succeeded):
        if hasattr(resource, 'session'):
            if not req_succeeded:
                resource.session.rollback()
            self.Session.remove()


app = falcon.API(middleware=[SQLAlchemySessionManager(Session)])

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    profiles = relationship("Profile", lazy='joined')

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

class ProfileSchema(ModelSchema):
    class Meta:
        model = Profile
        sqla_session = Session

class UserSchema(ModelSchema):
    profiles = fields.Nested(ProfileSchema, many=True)
    class Meta:
        model = User
        sqla_session = Session


user_schema = UserSchema()
profile_schema = ProfileSchema()

class UserResource:
    def on_get(self, req, resp):
        offset = req.get_param_as_int('offset') or 0
        limit = req.get_param_as_int('limit') or 3
        users = Session.query(User).limit(limit).offset(offset)
        data, errors = user_schema.dump(users, many=True)
        resp.status = falcon.HTTP_200
        if errors: 
            return json.dumps({"error": errors})
        resp.body = json.dumps(data, default=json_serial)


app.add_route('/users', UserResource())