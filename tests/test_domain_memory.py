from domain_memory import InMemoryUserLoginRepository


def test_in_memory_user_login_repository():
    repository = InMemoryUserLoginRepository()

    repository.add_user_login("123", "https://example.com")

    callback_url = repository.delete_user_login("123")
    assert callback_url == "https://example.com"

    callback_url = repository.delete_user_login("123")
    assert callback_url is None
