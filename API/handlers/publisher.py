from google.cloud import pubsub_v1


def publish_message(topic, message, PROJECT_ID):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, topic)
    future = publisher.publish(topic_path, message.encode("utf-8"))
    