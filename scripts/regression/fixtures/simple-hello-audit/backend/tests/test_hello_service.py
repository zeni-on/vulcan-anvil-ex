from app.services.hello_service import DefaultHelloService, HelloService


def test_UT_001_hello_service_contract_exists() -> None:
    service: HelloService = DefaultHelloService()

    assert callable(service.get_hello)


def test_UT_001_hello_service_returns_hello() -> None:
    service = DefaultHelloService()

    assert service.get_hello() == "hello"
