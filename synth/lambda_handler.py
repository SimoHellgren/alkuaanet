from base64 import b64encode
import json
from app.synth import make_opus_blob


def handler(event, context):
    body = json.loads(event.get("body"))
    tones = body.get("tones", [])
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "audio/ogg"},
        "body": b64encode(make_opus_blob(tones)),
    }
