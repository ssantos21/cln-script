from collections import defaultdict
from datetime import datetime, timedelta
import json
import requests

import utils

def execute(hours):
    settings_data = utils.get_settings_data()

    rpc_method = "v1/bkpr-channelsapy"

    url = "%s/%s" % (settings_data["nodeRestUrl"], rpc_method)

    headers = {
        "content-type": "application/json",
        "Rune": settings_data["rune"]
    }

    start_time = int((datetime.now() - timedelta(hours=hours)).timestamp())

    payload = { "start_time": start_time }

    response = requests.post(url, headers=headers, json=payload)

    return json.loads(response.text)

    # print(data)

if __name__ == "__main__":
    execute()
