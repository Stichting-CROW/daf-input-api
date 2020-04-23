import fastjsonschema
from flask import Flask, request, jsonify
import json
import mevent
import os
import psycopg2
import webhook_pusher
app = Flask(__name__)


conn_str = "dbname=daf2"

if "IP" in os.environ:
    conn_str += " host={} ".format(os.environ['IP'])
if "DB_PASSWORD" in os.environ:
    conn_str += " user=daf password={}".format(os.environ['DB_PASSWORD'])


conn = psycopg2.connect(conn_str)


f = open("dafs.schema", "r")
schemadict = json.loads(f.read())
event_validator = fastjsonschema.compile(schemadict)
output = webhook_pusher.WebHookPusher()
output.start()


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
    except fastjsonschema.JsonSchemaException e:
        return {'message': "Incorrect JSON input. [" + e.message + "]"}, 422
    
    msg = mevent.Event.insert(conn, data)
    if msg:
        output.enqueue(msg)
    return jsonify({"status": "created"})