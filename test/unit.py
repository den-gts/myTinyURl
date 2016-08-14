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
            mock_col.find_one = mock.Mock(return_value=future)
            return mock_col

        mock_db = mock.MagicMock(spec_set=dict)

        mock_db.__getitem__.side_effect = get_mock_collection
        tinyurld.app.bootstrap('D:\coding\myTinyURl/tinyurld\settings.py')
        self.db = mock_db
        return tinyurld.app.make_app(mock_db)

    def test_generate_tiny_url(self):
        word = '/some/res/1/'
        tiny = 'nu'
        response = self.fetch('/get_tiny/http://localhost{}'.format(word))
        self.db['settings'].update.assert_called_with(_id='counter', value=1457)
        self.db['links'].insert.assert_called_with(tiny=tiny, full=word)
        self.assertEqual(response, '<html><a href={0}>{0}</a></html>'.format(tiny).encode('utf-8'))
