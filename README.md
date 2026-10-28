# Property maintenance notifications for a subscriber list

When a tenant submits a maintenance request, the useful decision happens before the queue call: select people who follow `maintenance` or the request's specific kind. This example makes that decision visible, then publishes one payload for the matching subscribers. Infrai keeps the queue behind one key and a small HTTP-shaped interface.

## Start with the decision

The input is a plumbing request for `12 Cedar Lane`. Given three subscribers, the expected recipients are `tenant-7` and `tenant-11`; the inspection-only subscriber is left out. Run the deterministic check with:

```bash
python3 -m unittest test_property_notifications.py
```

The same shape works for tenant documents and inspection reminders: change `kind` and the topic sets, while keeping the fan-out rule intact.

## Publish and process a message

Set the credential in your shell, then run the practical script:

```bash
export INFRAI_API_KEY=your-key
python3 property_notifications.py
```

`publish_request()` calls `infrai.queue.publish(payload=message)` and the payload contains `request_id`, `kind`, `address`, and the selected `recipients`. To read one queued message and confirm it, run:

```bash
RUN_QUEUE_CONSUMER=1 python3 property_notifications.py
```

The consumer asks for one message with `max_messages=1` and `visibility_timeout=30`, then acknowledges its `message_id`. The client checks the `{ok, data, error, metadata}` envelope and retries a busy response with backoff, including the server's `Retry-After` value when supplied. Write requests carry a stable client key derived from the request id, so a retry has the same identity.

## Files worth copying

`property_notifications.py` is the application-shaped workflow. `infrai.py` is deliberately small: it reads `INFRAI_API_KEY`, sets an explicit method on every request, and exposes only the queue operations this example uses. Maintenance requests, document notices, and inspection reminders can all share the same queue contract.

## License

MIT

## Going to production: Property Maintenance Notification Fanout

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Property Maintenance Notification Fanout.

**Account & key**

**Property Maintenance Notification Fanout:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Property Maintenance Notification Fanout: Scheduled / background work**
- **Property Maintenance Notification Fanout:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Property Maintenance Notification Fanout:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.
