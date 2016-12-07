import unittest
import json
from app.consumer import Consumer
from tests.test_data import census_survey


class TestConsumer(unittest.TestCase):

    def setUp(self):
        self.consumer = Consumer()

    def test_get_processor_census(self):
        survey = json.loads(census_survey)
        processor = self.consumer.get_processor(survey)
        self.assertIsNotNone(processor)

    def test_get_processor_unknown(self):
        survey = json.loads(census_survey)
        survey['survey_id'] = "invalid"
        processor = self.consumer.get_processor(survey)
        self.assertIsNone(processor)
