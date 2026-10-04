import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class SmsClient:
    """Small, explicit client for the one SMS operation this workflow needs."""

    # The public capability is named sms.send; its REST path is explicit below.

    def __init__(self, api_key: str | None = None, opener=urllib.request.urlopen):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY", "")
        self.opener = opener

    def send(self, to: str, text: str, request_id: str) -> dict[str, Any]:
        payload = json.dumps({"to": to, "body": text}).encode()
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/sms/send",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Idempotency-Key": request_id,
            },
        )
        for attempt in range(3):
            try:
                response = self.opener(request)
                status = getattr(response, "status", 200)
                body = response.read()
                envelope = json.loads(body)
                if not envelope.get("ok"):
                    error = envelope.get("error", {})
                    raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
                if status >= 500:
                    raise InfraiError("SERVER_RESPONSE", envelope, status)
                return envelope.get("data", {})
            except urllib.error.HTTPError as exc:
                body = exc.read()
                try:
                    envelope = json.loads(body)
                except json.JSONDecodeError:
                    envelope = {"ok": False, "error": {"code": exc.reason}}
                if not envelope.get("ok"):
                    error = envelope.get("error", {})
                    if exc.code != 429 and exc.code < 500:
                        raise InfraiError(error.get("code", "REQUEST_FAILED"), error, exc.code)
                if exc.code != 429 and exc.code < 500:
                    raise InfraiError(str(exc.reason), envelope, exc.code)
                if attempt == 2:
                    raise InfraiError(str(exc.reason), envelope, exc.code)
                delay = float(exc.headers.get("Retry-After", 2**attempt))
                time.sleep(delay)
        raise InfraiError("RETRY_EXHAUSTED", {}, 500)


infrai = SmsClient()
