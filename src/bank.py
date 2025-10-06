from __future__ import annotations

class BankAccount:
    """
    Minimal bank account domain object with a simple ledger.

    Ledger entries are tuples:
      ("OPEN", opening_balance)
      ("DEPOSIT", amount)
      ("WITHDRAW", amount)
      ("TRANSFER_OUT", amount, other_owner)
      ("TRANSFER_IN", amount, other_owner)
    """

    def __init__(self, owner: str, opening_balance: float = 0.0) -> None:
        if not owner or not isinstance(owner, str):
            raise ValueError("owner must be a non-empty string")
        if opening_balance < 0:
            raise ValueError("opening_balance cannot be negative")
        self._owner = owner
        self._balance = float(opening_balance)
        self._ledger = [("OPEN", float(opening_balance))]

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> None:
        _validate_amount(amount)
        self._balance += amount
        self._ledger.append(("DEPOSIT", float(amount)))

    def withdraw(self, amount: float) -> None:
        _validate_amount(amount)
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
        self._ledger.append(("WITHDRAW", float(amount)))

    def transfer_to(self, other: "BankAccount", amount: float) -> None:
        if not isinstance(other, BankAccount):
            raise TypeError("other must be a BankAccount")
        self.withdraw(amount)  # raises if invalid/insufficient
        other.deposit(amount)
        self._ledger.append(("TRANSFER_OUT", float(amount), other.owner))
        other._ledger.append(("TRANSFER_IN", float(amount), self.owner))

    def statement(self):
        return list(self._ledger)

def _validate_amount(amount: float) -> None:
    if not isinstance(amount, (int, float)):
        raise TypeError("amount must be a number")
    if amount <= 0:
        raise ValueError("amount must be positive")

def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"
