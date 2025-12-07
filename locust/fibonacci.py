import random
from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(5, 10)

    @task
    def fibonacci(self):
        self.client.get("/fibonacci", params={"n": random.randint(0, 30)})
