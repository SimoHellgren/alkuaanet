from base64 import b64encode
import json
from app.synth import make_opus_blob


def handler(event, context):
    print(event)
    tones = event.get("tones", [])

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "audio/ogg"},
        "body": b64encode(make_opus_blob(tones)),
    }
