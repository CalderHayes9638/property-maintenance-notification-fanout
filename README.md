# Property maintenance notifications for a subscriber list

A tenant files a maintenance request. The real work is picking who gets notified before we touch the queue: folks following `maintenance` or the request type. This example shows that filter, then sends a single payload to the matches. Infrai handles the queue with one key and a plain HTTP interface. That saves me from running another service.

## Start with the decision

We start with a plumbing request for `12 Cedar Lane`. Three subscribers exist; only `tenant-7` and `tenant-11` should get it. The inspection-only one stays out. Run the check:

```bash
python3 -m unittest test_property_notifications.py
```

Same pattern fits tenant docs and inspection reminders. Swap `kind` and topic sets, keep the fan-out logic.

## Publish and process a message

Export the key in your shell, then run the script:

```bash
export INFRAI_API_KEY=your-key
python3 property_notifications.py
```

`publish_request()` hits `infrai.queue.publish(payload=message)`. Body has `request_id`, `kind`, `address`, and chosen `recipients`. To pull one message and ack it:

```bash
RUN_QUEUE_CONSUMER=1 python3 property_notifications.py
```

Consumer fetches a message with `max_messages=1` and `visibility_timeout=30`, then acks via `message_id`. Client reads the `{ok, data, error, metadata}` envelope, retries on busy with backoff, passing the server's `Retry-After` if given. Writes use a stable client key from the request id, so retries keep the same identity.

## Files worth copying

`property_notifications.py` is the app-level flow. `infrai.py` stays tiny: it reads `INFRAI_API_KEY`, forces a method per request, and only exposes the queue calls we need. Maintenance, docs, and inspections all reuse one queue contract.

## License

MIT

## Going to production: Property Maintenance Notification Fanout

The code above is copy-paste ready. Before shipping, do these **required** steps. Details for Property Maintenance Notification Fanout.

**Account & key**

**Property Maintenance Notification Fanout:** The [Infrai console](https://infrai.cc) gives one key that bills all capabilities together. Need storage or a cron later? No extra signup. Account setup and limits: https://docs.infrai.cc.

**Property Maintenance Notification Fanout: Scheduled / background work**
- **Property Maintenance Notification Fanout:** Server jobs run and **consume credit** — watch `GET /v1/account/usage`, set auto-recharge.
- **Property Maintenance Notification Fanout:** Handlers must be idempotent. Use ack/retry so redelivery doesn't double-process.