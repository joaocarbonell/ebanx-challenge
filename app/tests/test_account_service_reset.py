import pytest

from app.services.account_service import AccountService
from app.infrastructure.in_memory_account_repository import InMemoryAccountRepository
from app.domain.exceptions import AccountNotFound


class TestAccountServiceReset:

    def setup_method(self):
        """
        Runs before each test.
        Creates a fresh repository and service instance.
        """
        self.repository = InMemoryAccountRepository()
        self.service = AccountService(self.repository)

    def test_reset_should_clear_all_accounts(self):
        """
        Given existing accounts in the repository,
        When reset is called,
        Then all accounts should be removed.
        """

        # Create an account via deposit
        self.service.deposit(destination_id="100", amount=50)

        # Ensure account exists before reset
        balance_before = self.service.get_balance("100")
        assert balance_before == 50

        # Perform reset
        self.service.reset()

        # After reset, account should not exist
        with pytest.raises(AccountNotFound):
            self.service.get_balance("100")