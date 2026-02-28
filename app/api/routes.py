from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional


from app.services.account_service import AccountService
from app.infrastructure.in_memory_account_repository import InMemoryAccountRepository
from app.domain.exceptions import AccountNotFound, InsufficientFunds, NegativeValue

# Create a router for the API endpoints
router = APIRouter()

#Oringinal in-memory global state
repository = InMemoryAccountRepository()
service = AccountService(repository)

def get_service():
    return service

def get_repository():
    return repository

# Pydantic model for event request validation
class EventRequest(BaseModel):
    type: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    amount: int


# Endpoint to reset the application state
@router.post("/reset")
def reset(service: AccountService = Depends(get_service)):
    """
    Resets the application state.

    This endpoint resets the state of the application by calling the `reset` method
    of the `AccountService`. It is typically used to clear all data and return the
    application to its initial state.

    Returns:
        PlainTextResponse: A plain text response with a status code of 200 indicating
        that the reset operation was successful.
    """
    service.reset()
    return PlainTextResponse(content="OK", status_code=200)


# Endpoint to get the balance of an account
@router.get("/balance")
def get_balance(
    account_id: str,
    service: AccountService = Depends(get_service),
):
    """
    Retrieves the balance of a specific account.

    This endpoint fetches the balance of the account associated with the provided
    account ID. If the account exists, the balance is returned as plain text with
    a status code of 200. If the account does not exist, a status code of 404 is
    returned with a balance of "0".

    Parameters:
    ----------
    account_id : str
        The unique identifier of the account whose balance is to be retrieved.

    Returns:
    -------
    PlainTextResponse:
        - If the account exists: The balance as plain text with a 200 status code.
        - If the account does not exist: "0" as plain text with a 404 status code.
    """
    try:
        balance = service.get_balance(account_id)
        return PlainTextResponse(content=str(balance), status_code=200)
    except AccountNotFound:
        return PlainTextResponse(content="0", status_code=404)

#ToDo Implement other event types like transfer
# Endpoint to handle events (deposit and withdraw)
@router.post("/event", status_code=status.HTTP_201_CREATED)
def handle_event(
    event: EventRequest,
    service: AccountService = Depends(get_service),
):
    """
    Handles deposit and withdraw events.

    This endpoint processes financial events such as deposits and withdrawals. Based on the event type,
    it performs the corresponding operation and returns the updated account information. If the event
    type is invalid, or if the operation fails due to account not found or insufficient funds, an HTTP
    exception is raised.

    Parameters:
    ----------
    event : dict
        A dictionary containing the event details. It must include:
        - "type" (str): The type of the event ("deposit" or "withdraw").
        - "destination" (str, optional): The destination account ID for deposits.
        - "origin" (str, optional): The origin account ID for withdrawals.
        - "amount" (int): The amount to deposit or withdraw.

    Returns:
    -------
    dict:
        - For deposits: A dictionary with the destination account ID and updated balance.
        - For withdrawals: A dictionary with the origin account ID and updated balance.

    Raises:
    ------
    HTTPException:
        - 400: If the event type is invalid.
        - 404: If the account is not found or there are insufficient funds.
    """
    try:

        if event.type == "deposit":
            account = service.deposit(
                destination_id=event.destination,
                amount=event.amount,
            )
            return {
                "destination": {
                    "id": account.account_id,
                    "balance": account.balance,
                }
            }

        elif event.type  == "withdraw":
            account = service.withdraw(
                origin_id=event.origin,
                amount=event.amount,
            )
            return {
                "origin": {
                    "id": account.account_id,
                    "balance": account.balance,
                },
            }

        elif event.type == "transfer":
            if not event.origin or not event.destination:
                raise HTTPException(status_code=400, detail=0)

            origin, destination = service.transfer(
                origin_id=event.origin,
                destination_id=event.destination,
                amount=event.amount,
            )

            return {
                "origin": {
                    "id": origin.account_id,
                    "balance": origin.balance,
                },
                "destination": {
                    "id": destination.account_id,
                    "balance": destination.balance,
                },
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid event type")

    except AccountNotFound:
        return PlainTextResponse(content="0", status_code=404)

    except InsufficientFunds:
        return PlainTextResponse(content="0", status_code=404)

    except NegativeValue:
        raise HTTPException(status_code=400, detail="Amount must be positive")
