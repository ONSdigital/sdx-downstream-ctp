from app.settings import logger
from app.async_consumer import AsyncConsumer
from app.helpers.request_helper import get_doc_from_store
from .processor import CTPProcessor
from app import settings


def get_delivery_count_from_properties(properties):
    delivery_count = 0
    if properties.headers and 'x-delivery-count' in properties.headers:
        delivery_count = properties.headers['x-delivery-count']

    return delivery_count


class Consumer(AsyncConsumer):

    def on_message(self, unused_channel, basic_deliver, properties, body):
        logger.info('Received message', delivery_tag=basic_deliver.delivery_tag, app_id=properties.app_id, body=body.decode("utf-8"))

        delivery_count = get_delivery_count_from_properties(properties)
        delivery_count += 1

        try:
            mongo_id = body.decode("utf-8")
            document = get_doc_from_store(mongo_id)

            processor = self.get_processor(document)

            if processor:
                processed_ok = processor.process()

                if processed_ok:
                    self.acknowledge_message(basic_deliver.delivery_tag, tx_id=processor.tx_id)
                else:
                    if delivery_count == settings.QUEUE_MAX_MESSAGE_DELIVERIES:
                        logger.error("Reached maximum number of retries", tx_id=processor.tx_id, delivery_count=delivery_count, message=mongo_id)
                        self.reject_message(basic_deliver.delivery_tag, tx_id=processor.tx_id)
                    else:
                        pass

        except Exception as e:
            logger.error("ResponseProcessor failed", exception=e, tx_id=processor.tx_id)

    def get_processor(self, survey):
        if survey.get('survey_id') == 'census':
            return CTPProcessor(logger, survey)
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
