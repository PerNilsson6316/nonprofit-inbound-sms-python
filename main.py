import json
import sys

from src.infrai_sms import SmsClient
from src.workflow import InboundReply, handle


def main() -> None:
    raw = json.load(sys.stdin)
    reply = InboundReply(
        phone=raw["phone"], message=raw["message"], donor_name=raw.get("donor_name", "friend")
    )
    print(json.dumps(handle(reply, SmsClient()), ensure_ascii=True))


if __name__ == "__main__":
    main()
