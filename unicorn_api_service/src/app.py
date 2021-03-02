# Copyright 2014-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource

logger = logging.getLogger('root')
FORMAT = "%(levelname)s : %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
api = Api(app)

UNICORNS = {
    'unicorn1': {'name': 'fluffy rainbow', 'color': 'rainbow'},
    'unicorn2': {'name': 'shiny shine', 'color': 'sparkly yellow'},
    'unicorn3': {'name': 'princess twinkle toe', 'color': 'royal blue'}
}


def abort_if_unicorn_doesnt_exist(unicorn_id):
    if unicorn_id not in UNICORNS:
        logger.error(unicorn_id + 'does not exist')
        abort(404, message="{} doesn't exist".format(unicorn_id))


def abort_if_args_missing(args):
    if not args['name']:
        logger.error('Name argument missing')
        abort(400, message="Missing argument: name")
    if not args['color']:
        logger.error('Name argument missing!')
        abort(400, message="Missing argument: color")


parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('color')


class Unicorn(Resource):
    def get(self, unicorn_id):
        abort_if_unicorn_doesnt_exist(unicorn_id)
        logger.info("Request served!")
        return UNICORNS[unicorn_id]

    def delete(self, unicorn_id):
        abort_if_unicorn_doesnt_exist(unicorn_id)
        del UNICORNS[unicorn_id]
        return '', 204

    def put(self, unicorn_id):
        args = parser.parse_args()
        abort_if_args_missing(args)
        unicorn = {'name': args['name'], 'color': args['color']}
        UNICORNS[unicorn_id] = unicorn
        return unicorn, 201


class UnicornsList(Resource):
    def get(self):
        logger.info('Request served!!!')
        return UNICORNS

    def post(self):
        args = parser.parse_args()
        abort_if_args_missing(args)
        unicorn_id = int(max(UNICORNS.keys()).lstrip('unicorn')) + 1
        unicorn_id = 'unicorn%i' % unicorn_id
        UNICORNS[unicorn_id] = {'name': args['name'], 'color': args['color']}
        logger.info('Unicorn created!')
        return UNICORNS[unicorn_id], 201


class Health(Resource):
    def get(self):
        return 'Healthy', 200


@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())


api.add_resource(Health, '/health')
api.add_resource(UnicornsList, '/unicorns')
api.add_resource(Unicorn, '/unicorns/<unicorn_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80, debug=True)
