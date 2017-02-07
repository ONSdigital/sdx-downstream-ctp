import unittest
from unittest.mock import MagicMock
import mock
import json
import logging
from structlog import wrap_logger
from app.processor import CTPProcessor
from tests.test_data import census_survey
from app.helpers.sdxftp import SDXFTP

logger = wrap_logger(logging.getLogger(__name__))
ftp = SDXFTP(logger, "", "", "")


class TestCTPProcessor(unittest.TestCase):

    def setUp(self):
        survey = json.loads(census_survey)
        self.processor = CTPProcessor(logger, survey, ftp)

    def test_process_failure(self):
        with mock.patch('app.processor.get_sequence_no') as seq_mock:
            seq_mock.return_value = '1001'
            self.processor.deliver_file = MagicMock(return_value=False)
            result = self.processor.process()
            self.assertFalse(result)

    def test_process_success(self):
        with mock.patch('app.processor.get_sequence_no') as seq_mock:
            seq_mock.return_value = '1001'
            self.processor.deliver_file = MagicMock(return_value=True)
            result = self.processor.process()
            self.assertTrue(result)

    def test_name_replacer(self):
        filename = "12345.json"
        self.assertEqual(self.processor._get_completed_filename(filename), "12345.completed")
