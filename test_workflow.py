from src.workflow import InboundReply, decide


def test_reminder_reply_confirms_volunteer_shift():
    decision = decide(InboundReply(phone="+15550000000", message="REMINDER"))
    assert decision.kind == "volunteer_reminder"
    assert "confirmed" in decision.reply
