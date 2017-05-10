from app.helpers.request_helper import get_sequence_no
import json
from app import settings
import re
from app.helpers.exceptions import BadMessageError, RetryableError


class CTPProcessor(object):

    def __init__(self, logger, survey, ftpconn):
        self.logger = logger
        self.survey = survey
        self.tx_id = None
        self._setup_logger()
        self.ftp = ftpconn

    def process(self):
        sequence_no = get_sequence_no()
        if sequence_no is None:
            raise RetryableError("Failed to get sequence number")

        filename = '{}.json'.format(sequence_no)

        if self.survey is None:
            raise BadMessageError("No survey data")

        data = json.dumps(self.survey)

        # Attempt to deliver the real file and send a .completed after it
        self._deliver_file(filename, data)
        self._deliver_file(self._get_completed_filename(filename), "")

        return

    def _setup_logger(self):
        if self.survey:
            if 'metadata' in self.survey:
                metadata = self.survey['metadata']
                self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

            if 'tx_id' in self.survey:
                self.tx_id = self.survey['tx_id']
                self.logger = self.logger.bind(tx_id=self.tx_id)

    def _deliver_file(self, filename, data):
        self.logger.debug("Attempting to deliver to ftp", filename=filename)
        folder = self._get_ftp_folder(self.survey)

        try:
            self.ftp.deliver_binary(folder, filename, data.encode('utf-8'))
        except (RuntimeError, Exception) as e:
            self.logger.error("Failed to deliver file to ftp", filename=filename, exception=e)
            raise RetryableError("Failed to deliver file to ftp")

        self.logger.info("Delivered file to ftp", filename=filename)

    def _get_completed_filename(self, filename):
        return re.compile('.json$').sub('.completed', filename)

    def _get_ftp_folder(self, survey):
        if 'heartbeat' in survey and survey['heartbeat'] is True:
            return settings.FTP_HEARTBEAT_FOLDER
        else:
            return settings.FTP_FOLDER
