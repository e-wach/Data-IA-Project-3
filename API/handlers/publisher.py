from google.cloud import pubsub_v1
import os

# Sustituir por:  PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
PROJECT_ID = "original-list-459014-b6"

def publish_message(topic, message):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, topic)
    future = publisher.publish(topic_path, message.encode("utf-8"))
    