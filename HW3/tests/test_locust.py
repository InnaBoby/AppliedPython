from locust import HttpUser, between, task

# Определяем класс пользователя, наследуясь от HttpUser
class APIUser(HttpUser):
    host = "http://127.0.0.1:8000"            # базовый URL тестируемого API
    wait_time = between(1, 5)             # пауза между запросами от 1 до 5 секунд

    @task
    def list_items(self):
        self.client.get("/unauthenticated-route")



#RUN in CML:
#locust -f tests/test_locust.py