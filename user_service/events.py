import json
import sys

import pika
from loguru import logger


logger.add(sys.stderr, format="{level} {time} {message}", colorize=True, level="INFO")


def publish_user_delete_event(event):
    """
    Publishes a user deletion event to a RabbitMQ fanout exchange,
    broadcasting it to all consumers subscribed to the exchange.

    This function implements the publish side of the publish-subscribe
    pattern using a fanout exchange in RabbitMQ. The fanout exchange
    broadcasts messages to all queues bound to it, ensuring all
    subscribers receive the message. This is useful when multiple
    services need to act on the same event, such as logging or
    notifications.

    Args:
        event (dict): A dictionary containing details about the user
        deletion event. The dictionary will be serialized into a JSON
        format and published to the exchange. Example fields include
        user ID, timestamp, and deletion reason.

    Steps:
        1. Establishes a connection to the RabbitMQ server using
           `pika.BlockingConnection`.
        2. Declares a fanout exchange named "user_events_exchange". If
           it doesn't exist, RabbitMQ will create it.
        3. Publishes the event to the exchange, broadcasting it to all
           queues bound to this exchange. No routing key is needed for
           fanout exchanges, so an empty string `routing_key=""` is
           used.
        4. Closes the connection to RabbitMQ after the message is sent.

    Notes:
        - Consumers must bind their queues to the
          `user_events_exchange` to receive messages.
        - Fanout exchanges ensure each consumer subscribed to the
          exchange receives the message.

    Example:
        event_data = {
            "user_id": "12345",
            "timestamp": "2023-09-15T10:20:30",
            "reason": "user requested deletion"
        }

        publish_user_delete_event(event_data)
    """
    logger.info("publish_user_delete_event")

    # Establish a connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()

    # Declare a fanout exchange (broadcasts messages to all bound queues)
    channel.exchange_declare(
        exchange="user_events_exchange",
        exchange_type="fanout",
        # durable=True,
    )

    # Publish the event to the fanout exchange (no routing key needed for fanout)
    channel.basic_publish(
        exchange="user_events_exchange", routing_key="", body=json.dumps(event)
    )

    # Close the connection
    connection.close()
