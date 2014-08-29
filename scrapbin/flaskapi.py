
import logging

import flask
from flask import views
from flask import request

from scrapbin import api

LOG = logging.getLogger(__name__)


def loggingConfig():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(ch)


class RunAPI(views.MethodView):

    def post(self, node_id, run_id):
        LOG.info('POST : %s : %s' % (node_id, run_id))
        api.handle_request(request.environ)
        return '' # return 200 OK empty body


def add_routes(app):
    run_view = RunAPI.as_view('run_api')
    app.add_url_rule('/reports/nodes/<node_id>/runs',
                     defaults={'run_id': None},
                     view_func=run_view,
                     methods=['POST'])
    app.add_url_rule('/reports/nodes/<node_id>/runs/<run_id>',
                     view_func=run_view,
                     methods=['POST'])

def main():
    loggingConfig()
    app = flask.Flask('scrapbin')
    add_routes(app)
    app.run(port=5000)


if __name__ == '__main__':
    main()
