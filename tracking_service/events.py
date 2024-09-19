import json
import sys
import threading

import crud
import pika
from database import get_db
from loguru import logger


logger.add(sys.stderr, format="{level} {time} {message}", colorize=True, level="INFO")


def callback(ch, method, properties, body):
    """
    Callback function to handle messages from the RabbitMQ queue.

    This function processes messages by checking if the event type is
    "USER_DELETED". If so, it deletes user-related tracking data from
    the database using the provided user ID.

    Args:
        ch (BlockingChannel): The channel object.
        method (Basic.Deliver): Method frame containing delivery info.
        properties (BasicProperties): Properties of the message.
        body (bytes): The message body, containing the event data in JSON format.

    Returns:
        None
    """
    event = json.loads(body)
    user_id = int(event["user_id"])

    if event["type"] == "USER_DELETED":
        db = next(get_db())
        crud.delete_trackings_by_user(db, user_id)
        logger.info(f"Successfully deleted: {event['type']}")
    else:
        logger.info(f"Unknown event type: {event['type']}")


def consume_events() -> None:
    """
    Start consuming events from a queue bound to the 'user_events_exchange'
    fanout exchange in RabbitMQ.

    This function establishes a connection to the RabbitMQ server, declares
    a fanout exchange named 'user_events_exchange', creates an exclusive
    queue for the consumer, binds the queue to the fanout exchange, and
    starts consuming messages from the queue.

    The callback function is used to process incoming messages, and
    auto-acknowledgment is enabled to confirm message receipt.

    If the connection or consumption fails, an error is logged, and the
    process exits with status code 1.

    Returns:
        None
    """
    try:
        logger.info("Consumer is prepareing to consume events.")
        # Establish connection to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
        channel = connection.channel()

        # Declare the fanout exchange
        channel.exchange_declare(
            exchange="user_events_exchange", exchange_type="fanout"
        )

        # Declare an exclusive queue for this consumer and bind it to the exchange
        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange="user_events_exchange", queue=queue_name)

        # Start consuming messages from the queue
        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True
        )
        logger.info("Consumer is consuming events.")
        channel.start_consuming()
    except Exception:
        logger.error("Consumer could not start. Exiting.")
        exit(1)


def old_consume_events() -> None:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
        channel = connection.channel()
        channel.queue_declare(queue="user_events")
        channel.basic_consume(
            queue="user_events", on_message_callback=callback, auto_ack=True
        )
        channel.start_consuming()
        logger.info("Consumer is consuming events.")
    except Exception:
        print("Couldot start consumer")
        logger.error("Consumer Could not start. exit.")
        exit(1)


# Start the consumer in a separate thread
def start_consuming_events() -> None:
    print("start_consuming_events")
    logger.info("Starting consumer thread.")
    thread = threading.Thread(target=consume_events)
    thread.start()
