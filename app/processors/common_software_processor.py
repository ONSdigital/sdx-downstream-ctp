from app import settings
from app.helpers.request_helper import remote_call, response_ok, get_sequence_no
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

    def get_url(self):
        sequence_no = get_sequence_no()
        return "{0}/census/{1}".format(settings.SDX_TRANSFORM_CTP_URL, sequence_no)

    def transform(self):
        response = remote_call(self.get_url(), json=self.survey)
        if not response or not response_ok(response):
            return None

        return response.content

    def deliver_file(self, data):
        folder = get_ftp_folder(self.survey)
        return process_file_to_ftp(folder, data)

    def process(self):
        transformed = self.transform()

        if transformed is None:
            return False

        return self.deliver_file(transformed)
