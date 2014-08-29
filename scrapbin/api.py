
import gzip
import json
import logging
import re
import StringIO
from wsgiref import simple_server

from scrapbin import db

LOG = logging.getLogger(__name__)


class Node(object):

    def __init__(self, event, node_name):
        self.event = event
        self.node_name = node_name

    def write_out(self):
        filename = '%s.json' % self.node_name
        with open(filename, 'a') as node_json:
            json.dump(self.event, node_json)
            node_json.write('\n')
        LOG.info('Wrote data to %s' % filename)


def record_event(event_info, path_info):

    Node(event_info, path_info['node_name']).write_out()

    # save to database as well

    session = db.get_session()
    this_run = db.Run(id=event_info['run_id'],
                      node=path_info['node_name'],
                      **event_info)
    this_run = session.merge(this_run)
    session.commit()


def handle_request(environ, record=True):
    data = {'path': environ['PATH_INFO']}
    for k,v in environ.items():
        if 'HTTP' in k:
            LOG.debug('%s: %s' % (k,v))

    if environ.get('CONTENT_LENGTH'):
        content_length = int(environ.get('CONTENT_LENGTH'))
    else:
        content_length = 0

    if content_length > 0:
        body_stream = environ['wsgi.input']
        if environ.get('HTTP_CONTENT_ENCODING') == 'gzip':
            raw_data = StringIO.StringIO(body_stream.read(content_length))
            data['body'] = gzip.GzipFile(fileobj=raw_data).read()
        else:
            data['body'] = body_stream.read(content_length)


    LOG.debug(data)

    event_info = json.loads(data['body'])
    path_info = re.match('/reports/nodes/(?P<node_name>.+)/runs/?(?P<run_id>.+)?',
                         data['path']).groupdict()
    # path_info
    # {'node_name': 'somehost.example.com',
    #  'run_id': '121f4e67-5a0a-4456-b04d-42e00f92dc03'}

    if path_info.get('run_id'):
        event_info['run_id'] = path_info['run_id']

    LOG.debug('event_info: %s' % event_info)

    if record:
        record_event(event_info, path_info)


def sink_app(environ, start_response):
    status = '200 OK'
    headers = []
    start_response(status, headers)

    handle_request(environ)

    return ''


def main():
    logging.basicConfig()

    port = 5000
    httpd = simple_server.make_server('', port, sink_app)
    LOG.info('Starting server on port %s' % port)

    httpd.serve_forever()


if __name__ == '__main__':
    main()
