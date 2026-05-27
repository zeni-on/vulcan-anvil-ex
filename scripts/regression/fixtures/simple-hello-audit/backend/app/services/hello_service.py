from typing import Protocol


class HelloService(Protocol):
    """PGM-001 / IF-001: hello response public contract."""

    def get_hello(self) -> str:
        """REQ-001-01 / AC-001-02: return the hello response text."""


class DefaultHelloService:
    """Default HelloService implementation for PGM-001."""

    def get_hello(self) -> str:
        """REQ-001-01 / AC-001-02 / UT-001: return exactly hello."""
        return "hello"
