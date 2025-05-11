from google.cloud import pubsub_v1
import logging
import time


subscriber = pubsub_v1.SubscriberClient()


def listen_for_messages(callback_function, subscription_name, project_id):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_name)
    with subscriber:
        streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback_function)
        logging.info(f"Listening to {subscription_path}...")
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            streaming_pull_future.result(timeout=30)

