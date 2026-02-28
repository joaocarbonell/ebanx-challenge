import pytest

from app.services.account_service import AccountService
from app.infrastructure.in_memory_account_repository import InMemoryAccountRepository
from app.domain.exceptions import (
    AccountNotFound,
    InsufficientFunds,
    NegativeValue,
)


def create_service():
    repository = InMemoryAccountRepository()
    return AccountService(repository), repository


def test_transfer_from_non_existing_account_raises_exception():
    """
    Tests that transferring from a non-existing account raises AccountNotFound.
    """
    service, _ = create_service()

    with pytest.raises(AccountNotFound):
        service.transfer(origin_id="100", destination_id="200", amount=10)


def test_transfer_with_insufficient_funds_raises_exception():
    """
    Tests that transferring more than the available balance raises InsufficientFunds.
    """
    service, _ = create_service()

    service.deposit(destination_id="100", amount=10)

    with pytest.raises(InsufficientFunds):
        service.transfer(origin_id="100", destination_id="200", amount=20)


def test_transfer_creates_destination_account_if_not_exists():
    """
    Tests that transfer creates the destination account if it does not exist.
    """
    service, repository = create_service()

    service.deposit(destination_id="100", amount=50)

    origin, destination = service.transfer(
        origin_id="100",
        destination_id="200",
        amount=20,
    )

    assert origin.balance == 30
    assert destination.balance == 20

    assert repository.get("200") is not None
    assert repository.get("200").balance == 20


def test_transfer_subtracts_and_adds_balance_correctly():
    """
    Tests that transfer subtracts from origin and adds to destination correctly.
    """
    service, repository = create_service()

    service.deposit(destination_id="100", amount=100)
    service.deposit(destination_id="200", amount=10)

    origin, destination = service.transfer(
        origin_id="100",
        destination_id="200",
        amount=40,
    )

    assert origin.balance == 60
    assert destination.balance == 50

    assert repository.get("100").balance == 60
    assert repository.get("200").balance == 50


def test_transfer_with_negative_value_raises_exception():
    """
    Tests that transferring a negative amount raises NegativeValue.
    """
    service, _ = create_service()

    service.deposit(destination_id="100", amount=50)

    with pytest.raises(NegativeValue):
        service.transfer(origin_id="100", destination_id="200", amount=-10)