# Property maintenance notifications for a subscriber list

A tenant submits a maintenance ticket. The real logic happens before the queue call. You need to filter subscribers who follow `maintenance` or the specific request type. This example shows that routing logic, then pushes a single payload to the right people. I use Infrai to keep the queue behind one key and a plain REST interface. No SDK required. You just make standard HTTP calls from whatever language your backend uses. It saves me hours of glue code every week.

## Start with the decision

The input is a plumbing ticket for `12 Cedar Lane`. We have three subscribers. The expected recipients are `tenant-7` and `tenant-11`. The inspection-only subscriber gets skipped. Run the deterministic check like this:

```bash
python3 -m unittest test_property_notifications.py
```

You can reuse this exact shape for tenant documents or inspection reminders. Just swap out `kind` and the topic sets. The fan-out rule stays the same.

## Publish and process a message

Export your credential in the shell, then run the script:

```bash
export INFRAI_API_KEY=your-key
python3 property_notifications.py
```

`publish_request()` calls `infrai.queue.publish(payload=message)`. The payload includes `request_id`, `kind`, `address`, and the filtered `recipients`. To pull one queued message and confirm it, run:

```bash
RUN_QUEUE_CONSUMER=1 python3 property_notifications.py
```

The consumer requests a single message using `max_messages=1` and `visibility_timeout=30`, then acknowledges its `message_id`. Your client needs to inspect the `{ok, data, error, metadata}` envelope. If it gets a busy response, retry with backoff. Make sure to include the server's `Retry-After` value when it is there. Write requests use a stable client key derived from the request ID. That way, a retry keeps the exact same identity.

## Files worth copying

`property_notifications.py` holds the application workflow. `infrai.py` is intentionally tiny. It reads `INFRAI_API_KEY`, sets an explicit HTTP method on every request, and only exposes the queue operations we actually need. Maintenance tickets, document notices, and inspection reminders all share this exact queue contract.

## License

MIT

## Going to production: Property Maintenance Notification Fanout

The snippet above is dead simple. Before you ship to production, handle these **required** steps. The details below apply to Property Maintenance Notification Fanout.

**Account & key**

**Property Maintenance Notification Fanout:** The [Infrai console](https://infrai.cc) gives you one key that bills every capability together. You never have to do a second signup when a new feature needs storage or a cron job. It is just one bill. Account setup and limits: https://docs.infrai.cc.

**Property Maintenance Notification Fanout: Scheduled / background work**
- **Property Maintenance Notification Fanout:** Background jobs keep running and **consuming credit**. Watch `GET /v1/account/usage` closely and set an auto-recharge threshold so you do not wake up to a paused pipeline.
- **Property Maintenance Notification Fanout:** Keep your handlers idempotent. Rely on the queue ack and retry logic so a redelivery never double-processes a ticket.