import logging
import os
import threading
from queue import Queue

import requests

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10


class WebHookPusher:
    def __init__(self):
        self.q = Queue()
        self.session = requests.Session()

    def worker(self):
        while True:
            item = self.q.get()
            if item is None:
                break
            try:
                self.send_webhook(item)
            finally:
                self.q.task_done()

    # Don't use externally
    # This should be improved in the future.
    def send_webhook(self, msg):
        self.send_swap(msg)
        webhook_url = os.getenv("WEBHOOK_URL")
        if not webhook_url:
            logger.warning("WEBHOOK_URL is not configured, skipping webhook notification.")
            return
        try:
            r = self.session.post(webhook_url, json=msg, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            logger.error("Error sending webhook notification: %s", e)
            return
        if r.status_code != 200:
            logger.debug("Something went wrong sending push notification.")
        else:
            logger.debug("Succesfully sent webhook notification.")

    def send_swap(self, msg):
        if msg["bike"]["brand"] != "Swapfiets":
            return
        webhook_url = os.getenv("WEBHOOK_URL_SWAP")
        header = {"X-Api-Key": os.getenv("API_KEY_SWAP")}
        if not webhook_url:
            logger.warning("WEBHOOK_URL_SWAP is not configured, skipping swapfiets notification.")
            return
        try:
            r = self.session.post(webhook_url, json=msg, headers=header, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            logger.error("Error sending webhook notification to swapfiets: %s", e)
            return
        if r.status_code != 200:
            logger.debug("Something went wrong sending push notification to swapfiets.")
        else:
            logger.debug("Succesfully sent webhook notification to swapfiets.")

    def enqueue(self, msg):
        self.q.put(msg)

    def start(self):
        self.threads = []
        for _ in range(1):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            self.threads.append(t)

    def stop(self):
        for _ in range(1):
            self.q.put(None)
        for t in self.threads:
            t.join()
