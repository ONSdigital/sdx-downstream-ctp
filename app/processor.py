from app.helpers.request_helper import get_sequence_no
import json
from app import settings
import re


class CTPProcessor(object):

    def __init__(self, logger, survey, ftpconn):
        self.logger = logger
        self.survey = survey
        self.tx_id = None
        self.setup_logger()
        self.ftp = ftpconn

    def setup_logger(self):
        if self.survey:
            if 'metadata' in self.survey:
                metadata = self.survey['metadata']
                self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

            if 'tx_id' in self.survey:
                self.tx_id = self.survey['tx_id']
                self.logger = self.logger.bind(tx_id=self.tx_id)

    def deliver_file(self, filename, data):
        folder = self.get_ftp_folder(self.survey)
        return self.ftp.deliver_binary(folder, filename, data.encode('utf-8'))

    def process(self):
        filename = '{}.json'.format(get_sequence_no())
        data = json.dumps(self.survey)

        if data is None:
            return False

        # Attempt to deliver the real file and send
        # a .completed after it
        self.deliver_file(filename, data)

        completed_filename = filename
        p = re.compile('.json$')
        p.sub('.json', completed_filename)
        self.logger.info("Sending 'completed file'", filename=completed_filename)
        self.deliver_file(completed_filename, "")

        return

    def get_ftp_folder(self, survey):
        if 'heartbeat' in survey and survey['heartbeat'] is True:
            return settings.FTP_HEARTBEAT_FOLDER
        else:
            return settings.FTP_FOLDER
