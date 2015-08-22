import os, sys
import unittest
from time import time

sys.path.insert(0, sys.path[0]+"/..")

from harvest import HarvestClient, HarvestError

class TestHarvest(unittest.TestCase):

    HARVEST_URI = "https://goretoytest.harvestapp.com"

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

    def tearDown(self):
        pass

    def test_invalid_uri(self):
        try:
            HarvestClient("invalid_uri")
        except HarvestError as e:
            self.assertTrue(True)
        else:
            self.assertFalse(True, 'Wrong exception raised')

    def test_set_uri(self):
        self.assertEqual(self.basic_client.uri, self.HARVEST_URI)
        self.assertEqual(self.oauth_client.uri, self.HARVEST_URI)

    def test_set_oauth2(self):
        self.assertFalse(self.basic_client.oauth2, 'oauth2 property should False')
        self.assertTrue(self.oauth_client.oauth2, 'oauth2 property should True')

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
