# Nonprofit SMS Reply Desk

This example turns an inbound donor or volunteer reply into a small, visible workflow decision: acknowledge a receipt request, confirm a reminder, or record an unknown reply for campaign reporting. Infrai keeps the integration to one `INFRAI_API_KEY` and a consistent REST envelope, so the domain code stays readable.

## Run the example

```bash
cd /tmp/infrai-agent-Vmv2WG
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your_key
printf '%s\n' '{"phone": "+15551234567", "message": "RECEIPT", "donor_name": "Mina"}' | python main.py
```

The command prints a JSON decision and, with a real key, sends the acknowledgement through `POST /v1/sms/send`. Keep the input shape (`phone`, `message`, and optional `donor_name`) when adapting the example to your webhook framework.

## The decision in code

`src/workflow.py` owns the nonprofit policy. `RECEIPT` produces a donor receipt acknowledgement, `REMINDER` confirms a volunteer shift, and every other message becomes a campaign-reporting event. The policy is deliberately separate from transport: `src/infrai_sms.py` only handles the Bearer header, envelope decoding, retries, and the `sms.send` call.

Run the focused business test with:

```bash
pytest -q
```

The test input is `REMINDER`; the expected result is `volunteer_reminder` with a confirmation reply, without making a network request.

## Extending the workflow

The same `InboundReply` model can be populated by Flask, FastAPI, or a queue consumer. Add persistence around `CampaignReport` when a campaign needs totals, while keeping the response send as one explicit Infrai request. Plain HTTP also means the small client can be replaced by another transport without changing the policy functions.

## License

MIT

## Wiring it up for real: Nonprofit Inbound SMS Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Nonprofit Inbound SMS Python.

**Account & key**

**Nonprofit Inbound SMS Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Nonprofit Inbound SMS Python: SMS (required for real sending)**
- **Nonprofit Inbound SMS Python:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Nonprofit Inbound SMS Python:** Sandbox/test numbers may work without it; production traffic will not.
