import tornado.log  # TODO config log formater
from tornado.options import options
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, gen, os
import motor
import string
import tinyurld


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
        self.redirect(result['full'], True)


def bootstrap(config_file=None):
    options.define('config', config_file or tinyurld.default_config, type=str, help='Config file path')
    options.define('host', '0.0.0.0', type=str, help='Ip address for bind')
    options.define('port', 8888, type=int, help='application port')
    options.define('autoreload', False, type=bool,
                   help='Autoreload application after change files', group='application')
    options.define('debug', False, type=bool, help='Debug mode', group='application')
    options.define('mongo_host', type=str, help='MongoDB host IP', group='mongodb')
    options.define('mongo_port', 27017, type=int, help='MongoDB port', group='mongodb')
    options.define('mongo_user', None, type=str, help='MongoDB user', group='mongodb')
    options.define('mongo_password', None, type=str, help='MongoDB user password', group='mongodb')
    options.parse_command_line()

    options.parse_config_file(options.config)

    # override options from config file with command line args
    options.parse_command_line()
    tornado.log.app_log.info('Read config: {}'.format(options.config))


def connect_to_mongo():
    if options.mongo_user:
        mongo_auth = '{user}:{password}@'.format(user=options.mongo_user,
                                                 password=options.mongo_password)
    else:
        mongo_auth = ''
    mongo_url = 'mongodb://{auth}{host}:{port}'.format(host=options.mongo_host,
                                                       port=options.mongo_port,
                                                       auth=mongo_auth)
    tornado.log.app_log.info('Connect to {}'.format(mongo_url))
    client = motor.motor_tornado.MotorClient(mongo_url)
    tornado.log.app_log.info('Connected to mongoDB')
    return client


def make_app(database, opt_dict=None):
    opt_dict = opt_dict or {}
    app = Application([
            url(r'/get_tiny/(.*)', GetTynyHandler, dict(db=database)),
            url(r'/api/.*', ApiHandler),
            url(r'/(.+)', TinyUrlHandler, dict(db=database))
        ],
        **opt_dict
    )
    counter = IOLoop.instance().run_sync(lambda: database['settings'].find_one({'_id': 'counter'}))
    counter = counter['value'] if counter else 1
    app.counter = counter
    return app


def run_server():
    bootstrap()
    client = connect_to_mongo()
    database = client['tinyurld']
    app = make_app(database, options.group_dict('application'))
    tornado.log.app_log.info('Start application at {}:{} port'.format(options.host, options.port))
    app.listen(options.port, address=options.host)
    IOLoop.current().start()


if __name__ == '__main__':
    run_server()
