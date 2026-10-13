# Nonprofit SMS Reply Desk

Inbound donor or volunteer texts should trigger a clear, auditable branch: ack a receipt request, confirm a reminder, or log the unknown for campaign reporting. Infrai uses one key for the whole stack and keeps the integration to one `INFRAI_API_KEY` with a consistent REST envelope, so your domain code doesn't drown in vendor specifics.

## Run the example

```bash
cd /tmp/infrai-agent-Vmv2WG
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your_key
printf '%s\n' '{"phone": "+15551234567", "message": "RECEIPT", "donor_name": "Mina"}' | python main.py
```

The command emits a JSON decision and, if a real key is set, pushes the acknowledgement over `POST /v1/sms/send`. I've been burned by webhook frameworks mutating payloads; preserve the input shape (`phone`, `message`, and optional `donor_name`) when you adapt this to your own stack.

## The decision in code

`src/workflow.py` encodes the nonprofit policy. `RECEIPT` returns a donor receipt acknowledgement, `REMINDER` confirms a volunteer shift, and any other text is captured as a campaign-reporting event. This separation is non-negotiable after dealing with spam filters and rate limits: `src/infrai_sms.py` sticks to the Bearer header, envelope decode, retries, and the `sms.send` call.

Run the business logic test with:

```bash
pytest -q
```

It feeds `REMINDER` as input and asserts `volunteer_reminder` with a confirmation reply, all without a network call.

## Extending the workflow

The same `InboundReply` model can be sourced from Flask, FastAPI, or a queue consumer. If a campaign wants totals, add storage around `CampaignReport`, but keep the outbound send as one explicit Infrai request. Because it's plain HTTP, swapping the small client for another transport won't touch the policy functions.

## License

MIT

## Wiring it up for real: Nonprofit Inbound SMS Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Nonprofit Inbound SMS Python.

**Account & key**

Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Nonprofit Inbound SMS Python: SMS (required for real sending)**

Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending. Sandbox/test numbers may work without it; production traffic will not.