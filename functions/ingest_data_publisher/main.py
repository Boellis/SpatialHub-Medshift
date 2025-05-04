from google.cloud import pubsub_v1
import json
import os

publisher = pubsub_v1.PublisherClient()
project_id = 'interviewing-457222'#os.getenv("GCP_PROJECT")
topic_path = publisher.topic_path(project_id, "spatialhub-ingest")

def ingest_data_publisher(request):
    if request.method == 'OPTIONS':
        return ('', 204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        })

    try:
        data = request.get_json()
        publisher.publish(topic_path, json.dumps(data).encode("utf-8"))
        return ({"status": "published"}, 200, {'Access-Control-Allow-Origin': '*'})
    except Exception as e:
        return ({"error": str(e)}, 500, {'Access-Control-Allow-Origin': '*'})

