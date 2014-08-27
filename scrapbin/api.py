from wsgiref import simple_server
import gzip

import StringIO

import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

def sink_app(environ, start_response):
    status = '200 OK'
    headers = []
    start_response(status, headers)
    data = {'path': environ['PATH_INFO']}
    for k,v in environ.items():
        if 'HTTP' in k:
            LOG.info('%s: %s' % (k,v))

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

    LOG.info(data)
    return ''


def main():
    port = 5000
    httpd = simple_server.make_server('', port, sink_app)
    LOG.info('Starting server on port %s' % port)

    httpd.serve_forever()

if __name__ == '__main__':
    main()
