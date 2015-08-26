import os, sys
import unittest
from time import time

from mock import patch

sys.path.insert(0, sys.path[0]+"/..")

from harvest import HarvestClient, HarvestError, HTTPContentType, HTTPHeader, OauthKey

class TestHarvest(unittest.TestCase):

    HARVEST_URI = "https://goretoytest.harvestapp.com"
    TEST_ACCESS = 'access'
    TEST_REFRESH = 'refresh'

    def setUp(self):
        basic_kwargs = {
            'email': "tester@goretoy.com",
            'password': "tester account"
        }
        oauth2_kwargs = {
            'client_id': 'Unittest'
        }

        self.basic_client = HarvestClient(self.HARVEST_URI, **basic_kwargs)
        self.oauth_client = HarvestClient(self.HARVEST_URI, **oauth2_kwargs)

        TEST_ACCESS = self.TEST_ACCESS
        TEST_REFRESH = self.TEST_REFRESH
        class MockRsp:
            status_code = 200
            def json(self):
                return {OauthKey.ACCESS_TOKEN: TEST_ACCESS, OauthKey.REFRESH_TOKEN: TEST_REFRESH}
        self.mocked_rsp = MockRsp()

    def test_invalid_uri(self):
        with self.assertRaises(HarvestError):
            HarvestClient("invalid_uri")

    def test_set_uri(self):
        self.assertEqual(self.basic_client.uri, self.HARVEST_URI)
        self.assertEqual(self.oauth_client.uri, self.HARVEST_URI)

    def test_set_oauth2(self):
        self.assertFalse(self.basic_client.oauth2, 'oauth2 property should False')
        self.assertTrue(self.oauth_client.oauth2, 'oauth2 property should True')

    def test_oauth2_properties(self):
        self.assertIsNotNone(self.oauth_client.authorize_url, 'authorize_url not set in oauth2 client')
        self.assertNotEqual(self.oauth_client.authorize_data, {}, 'authorize_data not set in oauth2 client')
        self.assertEqual(self.basic_client.authorize_data, {}, 'authorize_data is set in basic client')
        self.assertIsNone(self.basic_client.authorize_url, 'authorize_url is set in basic client')

    def test_basic_properties(self):
        self.assertIsNotNone(self.basic_client.email, 'email not set on basic client')
        self.assertIsNotNone(self.basic_client.password, 'password not set on basic client')
        self.assertIsNone(self.oauth_client.email, 'email set on oauth client')
        self.assertIsNone(self.oauth_client.password, 'password set on oauth client')

    def test_set_content_type(self):
        self.assertEqual(self.basic_client.headers.get('Accept'), 'application/json', "Accept header not set correctly.")
        new_client = HarvestClient(self.HARVEST_URI, content_type='application/xml', client_id='Test')
        self.assertEqual(new_client.headers.get('Accept'), 'application/xml', "Accept header not set correctly.")

    def test_set_headers(self):
        self.assertIn('Authorization', self.basic_client.headers.keys(), 'Auth header not set in basic client.')
        self.assertNotIn('Authorization', self.oauth_client.headers.keys(), 'Auth header set in oauth client.')

    def test_set_encoded_type(self):
        self.basic_client.set_form_encoded_type()
        self.assertEqual(self.basic_client.headers.get(HTTPHeader.CONTENT_TYPE), HTTPContentType.FORM_ENCODED)

    def test_reset_content_type(self):
        self.test_set_encoded_type()
        self.basic_client.reset_content_type()
        self.assertEqual(self.basic_client.headers.get(HTTPHeader.CONTENT_TYPE), HTTPContentType.JSON)

    def test_get_oauth_tokens(self):
        with patch('requests.request', return_value=self.mocked_rsp) as get_tokens_mock:
            with self.assertRaises(HarvestError):
                self.basic_client.get_tokens('code', 'secret')
            access, refresh = self.oauth_client.get_tokens('code', 'secret')
            self.assertEqual(access, self.TEST_ACCESS)
            self.assertEqual(refresh, self.TEST_REFRESH)
            self.assertTrue(get_tokens_mock.called)

    def test_refresh_oauth_tokens(self):
        with patch('requests.request', return_value=self.mocked_rsp) as refresh_tokens_mock:
            with self.assertRaises(HarvestError):
                self.basic_client.refresh_tokens('code', 'secret')
            access, refresh = self.oauth_client.refresh_tokens('code', 'secret')
            self.assertEqual(access, self.TEST_ACCESS)
            self.assertEqual(refresh, self.TEST_REFRESH)
            self.assertTrue(refresh_tokens_mock.called)

    def test_response_is_successful(self):
        "No difference between the clients on this method."
        self.assertTrue(self.basic_client.response_is_successful(200))
        self.assertFalse(self.basic_client.response_is_successful(300))

    # def test_status_up(self):
    #     self.assertEqual("up", harvest.HarvestStatus().get(), "Harvest must be down?")

    # def test_status_not_down(self):
    #     self.assertNotEqual("down", harvest.HarvestStatus().get(), "Harvest must be down?")

    # def test_get_today(self):
    #     today = self.harvest.get_today()
    #     self.assertTrue(today.has_key("for_day"))

    # def test_add(self):
    #     today = self.harvest.get_today()
    #     start = time()
    #     project = "%s"%today['projects'][0]['id']
    #     task = "%s"%today['projects'][0]['tasks'][0]['id']
    #     self.assertTrue(self.harvest.add({
    #         "notes": "%s" % start,
    #         "hours": "1.5",
    #         "project_id": project,
    #         "task_id": task
    #     }))
    #     exists = self.harvest.get_today()

    #     #test that the entry got added
    #     self.assertTrue(len(exists['day_entries']) > len(today['day_entries']))

    #     if len(exists['day_entries']) > len(today['day_entries']):
    #         for entry in exists['day_entries']:
    #             if "%s"%entry['notes'] == "%s"%start:
    #                 self.assertEqual("1.5", "%s"%entry['hours'], "Hours are not equal")
    #                 self.assertEqual(project, "%s"%entry['project_id'], "Project Id not equal")
    #                 self.assertEqual(task, "%s"%entry['task_id'], "Task Id not equal")

if __name__ == '__main__':
    unittest.main()
