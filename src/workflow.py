from dataclasses import dataclass
from typing import Literal

from .infrai_sms import SmsClient


@dataclass(frozen=True)
class InboundReply:
    phone: str
    message: str
    donor_name: str = "friend"


@dataclass(frozen=True)
class Decision:
    kind: Literal["donor_receipt", "volunteer_reminder", "campaign_report"]
    reply: str


def decide(reply: InboundReply) -> Decision:
    keyword = reply.message.strip().upper()
    if keyword == "RECEIPT":
        return Decision("donor_receipt", f"Thanks {reply.donor_name}; your donation receipt is on its way.")
    if keyword == "REMINDER":
        return Decision("volunteer_reminder", "Your volunteer shift reminder is confirmed. Thank you!")
    return Decision("campaign_report", "Thanks for replying. Your message was recorded for the campaign team.")


def handle(reply: InboundReply, client: SmsClient) -> dict[str, str]:
    decision = decide(reply)
    client.send(reply.phone, decision.reply, request_id=f"inbound-{reply.phone}-{reply.message.strip().upper()}")
    return {"kind": decision.kind, "reply": decision.reply}
