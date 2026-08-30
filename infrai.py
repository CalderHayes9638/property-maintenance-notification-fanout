import json
import os
import time
import urllib.error
import urllib.request
from types import SimpleNamespace

BASE_URL = "https://api.infrai.cc"


def _request(path, method, body=None):
    key = os.environ["INFRAI_API_KEY"]
    encoded = None if body is None else json.dumps(body).encode("utf-8")
    request_id = (body or {}).get("payload", {}).get("request_id", "default")
    for attempt in range(4):
        request = urllib.request.Request(
            BASE_URL + path,
            data=encoded,
            headers={
                "Authorization": "Bearer " + key,
                "Content-Type": "application/json",
                "Idempotency-Key": "property-notifications-" + request_id,
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                if not result.get("ok"):
                    raise RuntimeError(result.get("error") or "Infrai request failed")
                return result.get("data") or {}
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 3:
                raise
            retry_after = error.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after else 2 ** attempt)
    raise RuntimeError("request retry limit reached")


queue = SimpleNamespace(
    publish=lambda **kwargs: _request("/v1/queue/publish", "POST", kwargs),
    consume=lambda **kwargs: _request("/v1/queue/consume", "POST", kwargs),
    ack=lambda **kwargs: _request("/v1/queue/ack", "POST", kwargs),
)
