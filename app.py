from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
import motor
import string
import random
MONGO_HOST = '10.250.216.67'

class GetTynyHandler(RequestHandler):
    def initialize(self, count, db):
        self.char_count = count
        self.db = db

    async def get(self, uri):
        word = [random.choice(string.ascii_letters+string.digits) for i in range(self.char_count)]
        word = ''.join(word)  # TODO Check for duplicate at database ?
        tiny_url = '{proto}://{host}/{word}'.format(proto=self.request.protocol,
                                                    host=self.request.host,
                                                    word=word)
        doc = {'tiny': word, 'full': uri}
        await self.db['links'].insert(doc)
        self.write(tiny_url.encode('utf-8'))  # TODO return formatted doc. etc html page or json response


class ApiHandler(RequestHandler):
    def get(self):
        self.write(self.request.uri.encode('utf-8'))


class TinyUrlHandler(RequestHandler):
    def initialize(self, db):
        self.db = db

    async def get(self, tiny_uri):
        query = {'tiny': tiny_uri}
        request = vars(self.request).copy()
        request['headers'] = vars(request['headers'])
        del request['connection']  # TODO implement recursive convertion all nested object to dict
        await self.db['log'].insert(request)

        result = await self.db['links'].find_one(query)   # TODO riase 404 error if result is empty
        self.redirect(result['full'])

if __name__ == '__main__':
    client = motor.motor_tornado.MotorClient(MONGO_HOST, 27017)
    database = client['myapp']
    app = Application([
        url(r'/get_tiny/(.*)', GetTynyHandler, dict(count=6, db=database)),
        url(r'/api/.*', ApiHandler),
        url(r'/(.{6})', TinyUrlHandler, dict(db=database))
        ])
    app.links = {}
    app.listen(8888)
    IOLoop.current().start()