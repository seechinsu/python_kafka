from sqlalchemy import create_engine
import falcon
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import settings
import json
from datetime import date, datetime

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

s = Session()

app = falcon.API()

class AgencyResource:
    def on_get(self, req, resp):

        results = s.execute('select * from users').fetchall()
        resp.status = falcon.HTTP_200
        resp.body = json.dumps([dict(result) for result in results], default=json_serial)

app.add_route('/agencies', AgencyResource())