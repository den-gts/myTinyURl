from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, gen
import motor
import string
from tinyurl import settings


class GetTynyHandler(RequestHandler):
    def initialize(self, db):
        self.db = db

    @staticmethod
    @gen.coroutine
    def _generate_tiny(number):
        pattern = string.digits + string.ascii_letters
        result = ''
        highest = number
        while highest:
            highest, lowest = divmod(highest, len(pattern))
            result += pattern[lowest]
        return result[::-1]

    @gen.coroutine
    def get(self, uri):
        word = yield self._generate_tiny(self.application.counter)
        self.application.counter += 1
        tiny_url = '{proto}://{host}/{word}'.format(proto=self.request.protocol,
                                                    host=self.request.host,
                                                    word=word)
        doc = {'tiny': word, 'full': uri}
        yield self.db['settings'].update({'_id': 'counter'},
                                         {'_id': 'counter', 'value': self.application.counter},
                                         upsert=True)
        yield self.db['links'].insert(doc)
        self.write('<html><a href={0}>{0}</a></html>'.format(tiny_url).encode('utf-8'))  # TODO use template


class ApiHandler(RequestHandler):
    def get(self):
        self.write(self.request.uri.encode('utf-8'))


class TinyUrlHandler(RequestHandler):
    def initialize(self, db):
        self.db = db

    @gen.coroutine
    def get(self, tiny_uri):
        query = {'tiny': tiny_uri}
        request = vars(self.request).copy()
        request['headers'] = vars(request['headers'])
        del request['connection']  # TODO implement recursive convertion all nested object to dict
        yield self.db['log'].insert(request)

        result = yield self.db['links'].find_one(query)
        if not result:
            self.send_error(status_code=404)
            return
        self.redirect(result['full'])


def run_server():
    client = motor.motor_tornado.MotorClient(settings.MONGO_HOST, settings.MONGO_PORT)
    database = client['myapp']

    app = Application([
        url(r'/get_tiny/(.*)', GetTynyHandler, dict(db=database)),
        url(r'/api/.*', ApiHandler),
        url(r'/(.+)', TinyUrlHandler, dict(db=database))
    ])
    counter = IOLoop.instance().run_sync(lambda: database['settings'].find_one({'_id': 'counter'}))
    counter = counter['value'] if counter else 1
    app.counter = counter
    app.listen(settings.APP_PORT)
    print('Start server at {} port'.format(settings.APP_PORT))
    IOLoop.current().start()

if __name__ == '__main__':
    run_server()
