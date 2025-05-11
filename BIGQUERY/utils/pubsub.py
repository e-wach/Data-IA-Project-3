from google.cloud import pubsub_v1
import logging


subscriber = pubsub_v1.SubscriberClient()


def listen_for_messages(callback_function, subscription_name, project_id):
    subscription_path = subscriber.subscription_path(project_id, subscription_name)
    logging.info(f"Listening to {subscription_path}...")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback_function)
    try:
        streaming_pull_future.result()
    except Exception as e:
        logging.error(f"Error while listening: {e}")
        streaming_pull_future.cancel()

