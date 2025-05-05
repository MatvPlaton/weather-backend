from typing import Optional

from domain import UserLoginRepository


class InMemoryUserLoginRepository(UserLoginRepository):

    def __init__(self):
        self.storage = {}

    def add_user_login(self, token: str, callback_url: str):
        self.storage[token] = callback_url

    def delete_user_login(self, token: str) -> Optional[str]:
        callback_url = self.storage.get(token)
        if callback_url is not None:
            del self.storage[token]
        return callback_url
