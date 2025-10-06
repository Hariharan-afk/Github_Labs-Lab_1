import unittest
from src.bank import BankAccount, format_currency

class TestBankAccount(unittest.TestCase):
    def setUp(self):
        self.alice = BankAccount("Alice", 100.0)
        self.bob = BankAccount("Bob", 50.0)

    def test_owner_and_opening_balance(self):
        self.assertEqual(self.alice.owner, "Alice")
        self.assertEqual(self.alice.balance, 100.0)

    def test_deposit(self):
        self.alice.deposit(25)
        self.assertEqual(self.alice.balance, 125.0)

    def test_withdraw_ok(self):
        self.alice.withdraw(60)
        self.assertEqual(self.alice.balance, 40.0)

    def test_withdraw_overdraft(self):
        with self.assertRaises(ValueError):
            self.alice.withdraw(1000)

    def test_transfer(self):
        self.alice.transfer_to(self.bob, 30)
        self.assertEqual(self.alice.balance, 70.0)
        self.assertEqual(self.bob.balance, 80.0)

    def test_format_currency(self):
        self.assertEqual(format_currency(1234.5), "$1,234.50")

if __name__ == "__main__":
    unittest.main()
