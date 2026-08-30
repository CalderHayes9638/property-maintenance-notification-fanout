import os
import infrai

QUEUE_NAME = "property-maintenance-notifications"


def subscribers_for(request, subscribers):
    """Choose recipients whose content preferences match a maintenance request."""
    wanted = {"maintenance", request["kind"]}
    return [subscriber for subscriber in subscribers if wanted.intersection(subscriber["topics"])]


def publish_request(request, subscribers):
    recipients = subscribers_for(request, subscribers)
    message = {
        "request_id": request["request_id"],
        "kind": request["kind"],
        "address": request["address"],
        "recipients": [subscriber["subscriber_id"] for subscriber in recipients],
    }
    if not recipients:
        return {"published": False, "reason": "no matching subscribers", "recipients": []}
    result = infrai.queue.publish(queue=QUEUE_NAME, payload=message)
    return {"published": True, "message": result, "recipients": message["recipients"]}


def consume_one():
    result = infrai.queue.consume(queue=QUEUE_NAME, max_messages=1, visibility_timeout=30)
    messages = result.get("messages") or []
    if not messages:
        return None
    message = messages[0]
    infrai.queue.ack(queue=QUEUE_NAME, message_id=message["message_id"])
    return message


if __name__ == "__main__":
    request = {"request_id": "repair-104", "kind": "plumbing", "address": "12 Cedar Lane"}
    subscribers = [
        {"subscriber_id": "tenant-7", "topics": {"maintenance", "plumbing"}},
        {"subscriber_id": "tenant-9", "topics": {"inspection"}},
    ]
    print(publish_request(request, subscribers))
    if os.environ.get("RUN_QUEUE_CONSUMER"):
        print(consume_one())
