from queue import Queue
import time
import threading
import requests
import logging
import os

class WebHookPusher():
    def __init__(self):
        self.q = Queue()
        self.logger = logging.getLogger()
        self.session = requests.Session()

    def worker(self):
        while True:
            item = self.q.get()
            if item is None:
                break
            self.send_webhook(item)
            self.q.task_done()

    # Don't use externally
    # This should be improved in the future.
    def send_webhook(self, msg):
        self.send_swap(msg)
        webhook_url = os.getenv("WEBHOOK_URL")
        try:
            r = self.session.post(webhook_url, json=msg)
        except requests.exceptions.RequestException as e:
            print("Error telegram webhook")
            print(e)
            return
        if r.status_code != 200:
            self.logger.debug("Something went wrong sending push notification.")
        else:
            self.logger.debug("Succesfully sent webhook notification.")

    def send_swap(self, msg):
        if msg["bike"]["brand"] != 'Swapfiets':
            return
        webhook_url = os.getenv("WEBHOOK_URL_SWAP")
        header = {"X-Api-Key": os.getenv("API_KEY_SWAP")}
        try:
            r = self.session.post(webhook_url, json=msg, headers=header)
        except requests.exceptions.RequestException as e:
           print("Error versturen webhook swap")
           print(e)
           return
        if r.status_code != 200:
            self.logger.debug("Something went wrong sending push notification to swapfiets.")
        else:
            self.logger.debug("Succesfully sent webhook notification to swapfiets.")

    def enqueue(self, msg):
        self.q.put(msg)

    def start(self):
        self.threads = []
        for _ in range(1):
            t = threading.Thread(target=self.worker)
            t.start()
            self.threads.append(t)

    def stop(self):
        for _ in range(1):
            self.q.put(None)
        for t in self.threads:
            t.join()
