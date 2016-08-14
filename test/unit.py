import mock
import tornado.gen
import tornado.testing
import tinyurld.app
from tornado.testing import AsyncHTTPTestCase


class TinyGeneartor(AsyncHTTPTestCase):
    def get_app(self):

        def get_mock_collection(col_name):
            mock_col = mock.Mock()
            future = tornado.gen.Future()
            future.set_result({'_id': 'counter', 'value': 1456})
            empty_future = tornado.gen.Future()
            empty_future.set_result(None)
            mock_col.find_one = mock.Mock(return_value=future)
            mock_col.update = mock.Mock(return_value=empty_future)
            mock_col.insert = mock.Mock(return_value=empty_future)
            return mock_col

        #mock_db = mock.MagicMock(spec_set=dict)

        #mock_db.__getitem__.side_effect = get_mock_collection

        mock_db = {'settings': mock.Mock(),
                   'links': mock.Mock()}
        future = tornado.gen.Future()
        future.set_result({'_id': 'counter', 'value': 1456})
        empty_future = tornado.gen.Future()
        empty_future.set_result(None)
        mock_db['settings'].find_one = mock.Mock(return_value=future)
        mock_db['settings'].update = mock.Mock(return_value=empty_future)
        mock_db['links'].insert = mock.Mock(return_value=empty_future)

        tinyurld.app.bootstrap('D:\coding\myTinyURl/tinyurld\settings.py')
        self.db = mock_db
        return tinyurld.app.make_app(mock_db)

    def test_generate_tiny_url(self):
        word = 'http://localhost/some/res/1/'
        tiny = 'nu'
        response = self.fetch('/get_tiny/{}'.format(word))
        self.db['settings'].update.assert_called_with({'_id': 'counter'},
                                                      {'_id': 'counter', 'value': 1457},
                                                      upsert=True)
        self.db['links'].insert.assert_called_with({'tiny': tiny,
                                                    'full': word})
        self.assertEqual(response.body,
                         '<html><a href={0}>{0}</a></html>'.format(tiny).encode('utf-8'))
