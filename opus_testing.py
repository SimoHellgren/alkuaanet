"""Testing for the lambda that creates opus files - should probably be handled with pytest.
   Also, funky differences between local testing and testing against actual aws service.
   Should rethink this when looking into setting up (local) dev environment.
"""

import requests
from base64 import b64decode
import json


def handle_aws(respnse):
    return b64decode(respnse.content)


def handle_local(response):
    data = response.json()
    return b64decode(data["body"])


if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv

    load_dotenv()

    _, *args = sys.argv

    # tones = {"tones": ["E4", "C4", "G3", "C3"]}
    tones = {"tones": ["B3"]}

    # test on aws by default
    if not args or args[0] == "aws":
        url = os.environ.get("SYNTH_URL_AWS")
        payload = json.dumps(tones)
        handler = handle_aws

    elif args[0] == "local":
        url = os.environ.get("SYNTH_URL_LOCAL")
        # I have no idea why this needs to be double encoded. For some reason
        # it behaves differently locally than on an actual lambda function
        payload = json.dumps({"body": json.dumps(tones)})
        handler = handle_local

    r = requests.post(url, headers={"Content-Type": "application/json"}, data=payload)

    data = handler(r)

    with open("hank.opus", "wb") as f:
        f.write(data)
