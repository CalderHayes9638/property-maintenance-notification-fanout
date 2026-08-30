import unittest

from property_notifications import subscribers_for


class SubscriberDecisionTest(unittest.TestCase):
    def test_plumbing_request_reaches_matching_subscribers(self):
        request = {"request_id": "repair-104", "kind": "plumbing", "address": "12 Cedar Lane"}
        subscribers = [
            {"subscriber_id": "tenant-7", "topics": {"maintenance", "plumbing"}},
            {"subscriber_id": "tenant-9", "topics": {"inspection"}},
            {"subscriber_id": "tenant-11", "topics": {"maintenance", "documents"}},
        ]
        selected = subscribers_for(request, subscribers)
        self.assertEqual(["tenant-7", "tenant-11"], [item["subscriber_id"] for item in selected])


if __name__ == "__main__":
    unittest.main()
