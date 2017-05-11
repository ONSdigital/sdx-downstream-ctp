from app import __version__
from app.settings import logger
from app.async_consumer import AsyncConsumer
from app.helpers.request_helper import get_doc_from_store
from .processor import CTPProcessor
from app import settings
from app.helpers.sftp import SFTP
from app.helpers.exceptions import BadMessageError, RetryableError
import os
import sys


def check_globals(module):
    g = {k: v for k, v in vars(module).items() if not k.startswith("_") and k.isupper()}
    return all(g.values())


def get_delivery_count_from_properties(properties):
    """
    Returns the delivery count for a message from the rabbit queue. The
    value is auto-set by rabbitmq.
    """
    delivery_count = 0
    if properties.headers and 'x-delivery-count' in properties.headers:
        delivery_count = properties.headers['x-delivery-count']
    return delivery_count + 1


class Consumer(AsyncConsumer):

    def __init__(self):
        self._ftp = SFTP(
            logger, settings.SFTP_HOST, settings.SFTP_USER,
            port=int(settings.SFTP_PORT), privKey=settings.SFTP_PRIVATEKEY_FILENAME
        )
        super(Consumer, self).__init__()

    def on_message(self, unused_channel, basic_deliver, properties, body):

        delivery_count = get_delivery_count_from_properties(properties)

        logger.info(
            'Received message',
            queue=self.QUEUE,
            delivery_tag=basic_deliver.delivery_tag,
            delivery_count=delivery_count,
            app_id=properties.app_id
        )

        mongo_id = body.decode("utf-8")
        document = get_doc_from_store(mongo_id)
        processor = CTPProcessor(logger, document, self._ftp)

        try:
            processor.process()
            self.acknowledge_message(basic_deliver.delivery_tag, tx_id=processor.tx_id)
            logger.info("Processed successfully", tx_id=processor.tx_id)

        except BadMessageError as e:
            # If it's a bad message then we have to reject it
            self.reject_message(basic_deliver.delivery_tag, tx_id=processor.tx_id)
            logger.error("Bad message", action="rejected", exception=e, delivery_count=delivery_count, tx_id=processor.tx_id)

        except (RetryableError, Exception) as e:
            self.nack_message(basic_deliver.delivery_tag, tx_id=processor.tx_id)
            logger.error("Failed to process", action="nack", exception=e, delivery_count=delivery_count, tx_id=processor.tx_id)


def main():
    logger.info("Starting consumer", version=__version__)
    check_default_env_vars()
    consumer = Consumer()
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()
