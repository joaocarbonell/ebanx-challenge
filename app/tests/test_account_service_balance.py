import pytest

from app.services.account_service import AccountService
from app.infrastructure.in_memory_account_repository import InMemoryAccountRepository
from app.domain.exceptions import AccountNotFound


class TestAccountServiceGetBalance:

    def setup_method(self):
        """
        Runs before each test.
        Creates a fresh repository and service instance.
        """
        self.repository = InMemoryAccountRepository()
        self.service = AccountService(self.repository)

    def test_get_balance_should_return_balance_when_account_exists(self):
        """
        Given an existing account,
        When get_balance is called,
        Then it should return the correct balance.
        """

        # Arrange
        self.service.deposit(destination_id="100", amount=75)

        # Act
        balance = self.service.get_balance("100")

        # Assert
        assert balance == 75

    def test_get_balance_should_raise_exception_when_account_does_not_exist(self):
        """
        Given a non-existing account,
        When get_balance is called,
        Then AccountNotFound should be raised.
        """

        with pytest.raises(AccountNotFound):
            self.service.get_balance("999")