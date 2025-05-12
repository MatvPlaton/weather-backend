from locust import HttpUser, task, between
import random
import uuid


class FastApiUser(HttpUser):
    wait_time = between(1, 2)

    demo_token = "6d060947-1ffe-4461-a868-b91367e909f9"
    authorization_token = "YOUR_TELEGRAM_SERVICE_HEADER_TOKEN"
    telegram_id = 958352999
    city = "Kazan"
    callback_url = "http://localhost:8501/login_success?token=5223d7f6-ea0d-4097-a7bf-7a660085cdbd&telegram_id=958352999&authorization_token=aab11f74-0d78-45d3-8c2c-c8bfa7864852"

    @task
    def test_weather_endpoint(self):
        self.client.get(
            f"/weather?city={self.city}&user_token={self.demo_token}"
        )

    @task
    def test_weather_history_endpoint(self):
        self.client.get(
            f"/weather/history?city={self.city}&limit=5&user_token={self.demo_token}"
        )

    @task
    def test_get_telegram_id(self):
        self.client.get(
            f"/user/telegram_id?user_token={self.demo_token}"
        )
