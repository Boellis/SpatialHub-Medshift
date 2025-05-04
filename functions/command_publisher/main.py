from google.cloud import pubsub_v1
import json
import os

publisher = pubsub_v1.PublisherClient()
project_id = 'interviewing-457222'  # or use os.getenv("GCP_PROJECT")
topic_path = publisher.topic_path(project_id, "command-sub")

def send_command(request):
    if request.method == 'OPTIONS':
        return ('', 204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        })

    try:
        data = request.get_json()
        command = data.get("command")
        hub_id = data.get("hub_id")

        if not command or not hub_id:
            return ({"error": "Missing 'command' or 'hub_id'"}, 400, {'Access-Control-Allow-Origin': '*'})

        message = json.dumps({
            "hub_id": hub_id,
            "command": command
        }).encode("utf-8")

        publisher.publish(topic_path, message)

        return ({"status": "command published"}, 200, {'Access-Control-Allow-Origin': '*'})
    except Exception as e:
        return ({"error": str(e)}, 500, {'Access-Control-Allow-Origin': '*'})
