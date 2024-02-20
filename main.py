import fastjsonschema
from flask import Flask, request, jsonify, g
import json
import mevent
import os
from psycopg2.pool import SimpleConnectionPool
import webhook_pusher
app = Flask(__name__)

f = open("dafs.schema", "r")
schemadict = json.loads(f.read())
event_validator = fastjsonschema.compile(schemadict)
output = webhook_pusher.WebHookPusher()
output.start()

conn_str = f"dbname={os.getenv('DB_NAME')}"

if "DB_HOST" in os.environ:
    conn_str += " host={} ".format(os.environ['DB_HOST'])
if "DB_USER" in os.environ:
    conn_str += " user={}".format(os.environ['DB_USER'])
if "DB_PASSWORD" in os.environ:
    conn_str += " password={}".format(os.environ['DB_PASSWORD'])
if "DB_PORT" in os.environ:
    conn_str += " port={}".format(os.environ['DB_PORT'])

pgpool = SimpleConnectionPool(minconn=1, 
        maxconn=5, 
        dsn=conn_str)

def get_db():
    if 'db' not in g:
        g.db = pgpool.getconn()
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        pgpool.putconn(db)

class InvalidUsage(Exception):
    status_code = 400
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/event',  methods=['POST'])
def input_event():
    data = request.get_json()
    if not data:
        return {'message': "Check if JSON is valid and correct application header is present."}, 400
    try:
        event_validator(data)
        print("ok")
    except fastjsonschema.JsonSchemaException as e:
        return {'message': "Incorrect JSON input. [" + e.message + "]"}, 422
    
    msg = mevent.Event.insert(get_db(), data)
    if msg:
        output.enqueue(msg)
    return jsonify({"status": "created"})