from app.helpers.request_helper import get_sequence_no
from app.helpers.ftp_helper import get_ftp_folder, process_file_to_ftp


class CTPProcessor(object):

    def __init__(self, logger, survey):
        self.logger = logger
        self.survey = survey
        self.tx_id = None
        self.setup_logger()

    def setup_logger(self):
        if self.survey:
            if 'metadata' in self.survey:
                metadata = self.survey['metadata']
                self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

            if 'tx_id' in self.survey:
                self.tx_id = self.survey['tx_id']
                self.logger = self.logger.bind(tx_id=self.tx_id)

    def deliver_file(self, data):
        folder = get_ftp_folder(self.survey)
        return process_file_to_ftp(folder, data)

    def process(self):
        filename = '{}.json()'.format(get_sequence_no())
        data = self.survey

        if data is None:
            return False

        return self.deliver_file(filename, data)
