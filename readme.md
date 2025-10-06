# Github_Labs-Lab_1: Mini Bank Account Library — CSV I/O + Tests + CI

A tiny, test-friendly Python project that models simple bank accounts, supports CSV import/export, and includes both pytest and unittest test suites. It demonstrates core lab skills: virtual environments, clean repo structure, automated tests, and GitHub Actions CI with coverage.

## 🚀 What this mini project does

- Implements a `BankAccount` class with a simple ledger of events (`OPEN`, `DEPOSIT`, `WITHDRAW`, `TRANSFER_OUT`, `TRANSFER_IN`)
- Provides CSV I/O to:
  - load accounts (`accounts.csv`)
  - apply ordered transactions (`transactions.csv`)
  - export current balances (`balances.csv`)
  - export all post-apply transactions (`all_tx.csv`)
- Includes two test suites (pytest + unittest)
- GitHub Actions CI runs both test suites; pytest also reports coverage

## 📦 Purpose & What's Included

**Purpose:** hands-on practice with Python project hygiene, testing, and CI.

**Included:**
- `src/bank.py` — core logic (BankAccount, validation, ledger)
- `src/io_csv.py` — BOM/whitespace/delimiter-tolerant CSV import/export + CLI
- `test/` — pytest + unittest suites
- `.github/workflows/` — CI for pytest (with coverage) and unittest
- `data/` — sample CSVs you can run locally (inputs) plus generated outputs

## 🧰 Requirements

- **Python:** 3.11
- **OS:** Windows, macOS (works on Linux too)
- **Virtual env name (examples):** `lab_01`

## 🗂️ Project Structure

```
.
├─ data/
│  ├─ accounts.csv            # input: owner,opening_balance
│  ├─ transactions.csv        # input: owner,event,amount,other
│  ├─ balances.csv            # output after apply (owner,balance)
│  └─ all_tx.csv              # output after apply (owner,event,amount,other)
├─ src/
│  ├─ __init__.py
│  ├─ bank.py                 # BankAccount class + helpers
│  └─ io_csv.py               # CSV I/O + CLI
├─ test/
│  ├─ test_pytest.py          # pytest unit tests
│  ├─ test_io_pytest.py       # pytest CSV I/O tests
│  └─ test_unittest.py        # unittest unit tests
├─ .github/workflows/
│  ├─ pytest_action.yml       # "Testing with Pytest"
│  └─ unittest_action.yml     # "Python Unittests"
├─ requirements.txt
└─ README.md
```

## 🐍 Setup

### Windows (PowerShell)

```powershell
python -m venv lab_01
lab_01\Scripts\activate
pip install -r requirements.txt
```

### macOS

```bash
python3 -m venv lab_01
source lab_01/bin/activate
pip install -r requirements.txt
```


## 🧩 Python API (example)

```python
from src.bank import BankAccount

alice = BankAccount("Alice", 100)
bob = BankAccount("Bob", 50)
alice.deposit(20)
alice.withdraw(10)
alice.transfer_to(bob, 40)

print(alice.balance)  # 70.0
print(bob.balance)    # 90.0
print(alice.statement())
```

## 📄 CSV Schemas

### accounts.csv

**Headers:** `owner,opening_balance`

**Example rows:**

```csv
owner,opening_balance
Alice,100
Bob,50
```

### transactions.csv

**Headers:** `owner,event,amount,other`

**event** ∈ `{DEPOSIT, WITHDRAW, TRANSFER_OUT, TRANSFER_IN}`

**Example rows:**

```csv
owner,event,amount,other
Alice,DEPOSIT,20,
Alice,WITHDRAW,10,
Alice,TRANSFER_OUT,40,Bob
```

> **Note:** `TRANSFER_IN` is auto-created when a matching `TRANSFER_OUT` is applied. If you include both, duplicates are safely ignored.

## 🖥️ CLI Usage

The CLI is built into `src/io_csv.py`.

### Apply transactions and export balances

```bash
python -m src.io_csv apply \
  --accounts data/accounts.csv \
  --transactions data/transactions.csv \
  --out-balances data/balances.csv
```

### Dump all ledgers after applying

```bash
python -m src.io_csv dump-ledgers \
  --accounts data/accounts.csv \
  --transactions data/transactions.csv \
  --out-ledgers data/all_tx.csv
```

### Example outputs

**balances.csv:**

```csv
owner,balance
Alice,70.0
Bob,90.0
```

**all_tx.csv:**

```csv
owner,event,amount,other
Alice,OPEN,100.0,
Alice,DEPOSIT,20.0,
Alice,WITHDRAW,10.0,
Alice,TRANSFER_OUT,40.0,Bob
Bob,OPEN,50.0,
Bob,TRANSFER_IN,40.0,Alice
```

## ✅ Running Tests

### Pytest

```bash
pytest -q
```
output:
```bash
(lab_01) PS C:\Users\suraj\Hariharan\Assignments\Term3\MLOps\mlops_labs\github_lab> pytest -q
...................                                                                                                                                                                                                                                                  [100%] 
...................                                                                                                                                                                                                                                                  [100%] 
19 passed in 0.02s
```
### Unittest

```bash
python -m unittest discover -s test -p "test_unittest.py" -v
```
output:
```bash
(lab_01) PS C:\Users\suraj\Hariharan\Assignments\Term3\MLOps\mlops_labs\github_lab> python -m unittest discover -s test -p "test_unittest.py"
......
......
----------------------------------------------------------------------
----------------------------------------------------------------------
Ran 6 tests in 0.001s
```
## 🔄 GitHub Actions (CI) & Badges

**Workflows:**
- Testing with Pytest (coverage on `src/`)
- Python Unittests

Replace `<YOUR_GH_USER>` and `<YOUR_REPO>` below after you push:

```markdown
[![Testing with Pytest](https://github.com/<YOUR_GH_USER>/<YOUR_REPO>/actions/workflows/pytest_action.yml/badge.svg)](../../actions/workflows/pytest_action.yml)
[![Python Unittests](https://github.com/<YOUR_GH_USER>/<YOUR_REPO>/actions/workflows/unittest_action.yml/badge.svg)](../../actions/workflows/unittest_action.yml)
```

Coverage is reported in the pytest job (terminal and optional XML artifact).

## 🧠 Design Notes

- **Robust CSV parsing:** handles UTF-8 BOM (`utf-8-sig`), trims spaces, sniffs delimiters; skips blank lines; normalizes header case
- **Validation:** non-empty owner, positive amounts, overdraft protection, type checks
- **Transfer idempotence:** if both `TRANSFER_OUT` and `TRANSFER_IN` lines appear, double-application is avoided
- **Separation of concerns:** core logic (`bank.py`) vs I/O (`io_csv.py`) vs tests

## 🛠️ Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

Run commands from the repo root; ensure `src/__init__.py` exists. In CI, we set `PYTHONPATH=.` (pytest) and scope unittest discovery.

### `KeyError: 'owner'` when loading CSV

Usually header whitespace/BOM/different delimiter—our robust loader handles this. Ensure your headers match the schemas exactly.

## 🎯 Lab Objectives Mapping

- ✅ Virtual environment (`lab_01`)
- ✅ GitHub repo hygiene & structure (`src/`, `test/`, `.github/workflows/`)
- ✅ Python modules & CLI (`bank.py`, `io_csv.py`)
- ✅ Tests (pytest + unittest)
- ✅ CI (Actions: Testing with Pytest, Python Unittests) with coverage


## 👤 Author

Hariharan Chandrasekar (NUID: 002312867)

---

## Quick Commands (Cheat Sheet)

```bash
# venv
python -m venv lab_01 && lab_01\Scripts\activate    # Windows
python3 -m venv lab_01 && source lab_01/bin/activate # macOS

# install
pip install -r requirements.txt

# run tests
pytest -q
python -m unittest discover -s test -p "test_unittest.py" -v

# csv cli
python -m src.io_csv apply --accounts data/accounts.csv --transactions data/transactions.csv --out-balances data/balances.csv
python -m src.io_csv dump-ledgers --accounts data/accounts.csv --transactions data/transactions.csv --out-ledgers data/all_tx.csv
```