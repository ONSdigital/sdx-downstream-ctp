import unittest
import mock
import json
import logging
from structlog import wrap_logger
from app.processor import CTPProcessor
from tests.test_data import census_survey
from requests import Response
from app.helpers.sdxftp import SDXFTP
from app.helpers.exceptions import BadMessageError, RetryableError

logger = wrap_logger(logging.getLogger(__name__))
ftp = SDXFTP(logger, "", "", "")


class TestCTPProcessor(unittest.TestCase):

    def setUp(self):
        survey = json.loads(census_survey)
        self.processor = CTPProcessor(logger, survey, ftp)

    def _get_response(self):
        response = Response()
        response.status_code = 200
        response._content = b'Some content'
        return response

    def test_sequence(self):
        with mock.patch('app.processor.get_sequence_no') as seq_mock:

            with mock.patch('app.helpers.sdxftp.SDXFTP.deliver_binary') as ftp_mock:
                ftp_mock.return_value = True

                response = self._get_response()
                with mock.patch('app.helpers.request_helper.remote_call') as call_mock:
                    call_mock.return_value = response

                    # Good return
                    seq_mock.return_value = '1001'
                    self.processor.process()

                    # Call issue
                    seq_mock.return_value = None
                    with self.assertRaises(RetryableError):
                        self.processor.process()

    def test_ftp(self):
        with mock.patch('app.processor.get_sequence_no') as seq_mock:
            seq_mock.return_value = '1001'

            response = self._get_response()
            with mock.patch('app.helpers.request_helper.remote_call') as call_mock:
                call_mock.return_value = response

                with mock.patch('app.helpers.sdxftp.SDXFTP.deliver_binary') as ftp_mock:

                    # Good deliver
                    self.processor.process()

                    # Failed deliver
                    ftp_mock.side_effect = RuntimeError
                    with self.assertRaises(RetryableError):
                        self.processor.process()

    def test_bad_data(self):
        with mock.patch('app.processor.get_sequence_no') as seq_mock:
            seq_mock.return_value = '1001'

            with mock.patch('app.helpers.sdxftp.SDXFTP.deliver_binary') as ftp_mock:
                ftp_mock.return_value = True

                # Empty data
                local_processor = CTPProcessor(logger, None, ftp)
                with self.assertRaises(BadMessageError):
                    local_processor.process()

    def test_name_replacer(self):
        filename = "12345.json"
        self.assertEqual(self.processor._get_completed_filename(filename), "12345.completed")
