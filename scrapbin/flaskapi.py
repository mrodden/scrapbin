
import logging

import flask
from flask import views
from flask import request
from flask import json

from scrapbin import api
from scrapbin import db

LOG = logging.getLogger(__name__)


def loggingConfig():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(ch)


class ScrapbinJsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, db.Run):
            return o.to_json()
        return json.JSONEncoder.default(self, o)


class RunAPI(views.MethodView):

    def post(self, node_id, run_id):
        LOG.info('POST : %s : %s' % (node_id, run_id))
        api.handle_request(request.environ)
        return '' # return 200 OK empty body

class ReportAPI(views.MethodView):

    def get(self):
        status = request.args.get('status')
        since_time = request.args.get('since')

        ses = db.get_session()
        query = ses.query(db.Run)

        if status:
            query = query.filter(db.Run.status == status)

        if since_time:
            query = query.filter(db.Run.start_time > since_time)

        results = query.all()

        json_results = json.dumps(results, cls=ScrapbinJsonEncoder)
        return json_results


def add_routes(app):
    run_view = RunAPI.as_view('run_api')
    report_view=ReportAPI.as_view('report_api')
    app.add_url_rule('/reports/nodes/<node_id>/runs',
                     defaults={'run_id': None},
                     view_func=run_view,
                     methods=['POST'])
    app.add_url_rule('/reports/nodes/<node_id>/runs/<run_id>',
                     view_func=run_view,
                     methods=['POST'])
    app.add_url_rule('/reports/',
                     view_func=report_view,
                     methods=['GET'])

def main():
    loggingConfig()
    app = flask.Flask('scrapbin')
    add_routes(app)
    app.run(port=5000)


if __name__ == '__main__':
    main()
