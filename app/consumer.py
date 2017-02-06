from app.settings import logger
from app.async_consumer import AsyncConsumer
from app.helpers.request_helper import get_doc_from_store
from .processor import CTPProcessor
from app import settings
from app.helpers.sdxftp import SDXFTP


class Consumer(AsyncConsumer):

    def __init__(self):
        self._ftp = SDXFTP(logger, settings.FTP_HOST, settings.FTP_USER, settings.FTP_PASS)
        super(Consumer, self).__init__()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        logger.info("Received message", queue=self.QUEUE, delivery_tag=basic_deliver.delivery_tag, app_id=properties.app_id)

        try:
            tx_id = body.decode("utf-8")
            document = get_doc_from_store(tx_id)

            processor = self.get_processor(document)

            processed_ok = processor.process()

            if processed_ok:
                logger.info("Processed successfully", tx_id=processor.tx_id)
                self.acknowledge_message(basic_deliver.delivery_tag, tx_id=processor.tx_id)

        except Exception as e:
            logger.error("ResponseProcessor failed", exception=e, tx_id=document['tx_id'])

    def get_processor(self, survey):
        if survey.get('survey_id') == 'census':
            return CTPProcessor(logger, survey, self._ftp)
        else:
            logger.error("Missing or not supported survey id")
            return None


def main():
    logger.debug("Starting consumer")
    consumer = Consumer()
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()
