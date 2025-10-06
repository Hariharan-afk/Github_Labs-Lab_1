import pytest
from src.bank import BankAccount, format_currency

@pytest.fixture
def alice():
    return BankAccount("Alice", 100.0)

@pytest.fixture
def bob():
    return BankAccount("Bob", 50.0)

def test_opening_balance_and_owner(alice):
    assert alice.owner == "Alice"
    assert alice.balance == 100.0
    assert ("OPEN", 100.0) in alice.statement()

@pytest.mark.parametrize("amount,expected", [
    (1, "$1.00"),
    (1234.5, "$1,234.50"),
    (9999999.999, "$10,000,000.00"),
])
def test_format_currency(amount, expected):
    assert format_currency(amount) == expected

def test_deposit_updates_balance_and_ledger(alice):
    alice.deposit(20)
    assert alice.balance == 120.0
    assert ("DEPOSIT", 20.0) in alice.statement()

def test_withdraw_valid(alice):
    alice.withdraw(30)
    assert alice.balance == 70.0
    assert ("WITHDRAW", 30.0) in alice.statement()

def test_withdraw_insufficient_funds_raises(alice):
    with pytest.raises(ValueError, match="insufficient"):
        alice.withdraw(1000)

@pytest.mark.parametrize("bad", [0, -1, -0.01])
def test_invalid_amounts_raise_on_deposit(alice, bad):
    with pytest.raises(ValueError):
        alice.deposit(bad)

def test_transfer_between_accounts(alice, bob):
    alice.transfer_to(bob, 40)
    assert alice.balance == 60.0
    assert bob.balance == 90.0
    assert any(t[0] == "TRANSFER_OUT" and t[1] == 40.0 and t[2] == "Bob" for t in alice.statement())
    assert any(t[0] == "TRANSFER_IN"  and t[1] == 40.0 and t[2] == "Alice" for t in bob.statement())
