from __future__ import annotations
from pathlib import Path
import csv
from typing import Dict, Iterable, List, Tuple
from .bank import BankAccount


# --- helpers to make CSV reading robust ---
def _open_csv_text(path):
    # utf-8-sig strips BOM if present (common from Excel)
    return open(path, newline="", encoding="utf-8-sig")

def _csv_reader_with_sniff(file_obj):
    # Try to sniff delimiter; fall back to comma
    head = file_obj.read(2048)
    file_obj.seek(0)
    try:
        dialect = csv.Sniffer().sniff(head)
        return csv.DictReader(file_obj, dialect=dialect)
    except Exception:
        return csv.DictReader(file_obj)  # default comma

def export_accounts_to_csv(accounts: Iterable[BankAccount], out_csv: str | Path) -> None:
    """
    Export current balances to CSV with schema:
      owner,balance
    """
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["owner", "balance"])
        writer.writeheader()
        for a in accounts:
            writer.writerow({"owner": a.owner, "balance": f"{a.balance:.2f}"})


# ---------------------------
# Accounts import / export
# ---------------------------

def load_accounts_from_csv(accounts_csv: str | Path) -> Dict[str, BankAccount]:
    """
    Load accounts from CSV. Accepts flexible headers (case/space/BOM tolerant):
      owner, opening_balance
    """
    accounts: Dict[str, BankAccount] = {}
    with _open_csv_text(accounts_csv) as f:
        reader = _csv_reader_with_sniff(f)

        if not reader.fieldnames:
            raise ValueError("accounts.csv appears empty or has no header row.")

        # normalize headers
        norm_fields = [fn.strip().lower() for fn in reader.fieldnames]
        mapper = {orig: norm for orig, norm in zip(reader.fieldnames, norm_fields)}

        required = {"owner", "opening_balance"}
        if not required.issubset(set(norm_fields)):
            raise ValueError(
                f"accounts.csv missing required headers {required}. Found: {norm_fields}"
            )

        for row in reader:
            # skip blank lines cleanly
            if row is None or all((v is None or str(v).strip() == "") for v in row.values()):
                continue
            # normalize row keys/values
            nrow = {
                mapper[k]: (v.strip() if isinstance(v, str) else v)
                for k, v in row.items() if k is not None
            }

            owner = nrow["owner"]
            opening_balance = float(nrow["opening_balance"])
            if not owner:
                raise ValueError("Empty owner name in accounts.csv")
            if owner in accounts:
                raise ValueError(f"Duplicate owner in accounts.csv: {owner}")
            accounts[owner] = BankAccount(owner, opening_balance)
    return accounts


# ---------------------------
# Transactions import/export
# ---------------------------

def export_ledger_to_csv(account: BankAccount, out_csv: str | Path) -> None:
    """
    Export a single account ledger (schema: event,amount,other)
    Opening event is omitted (accounts.csv handles OPEN).
    """
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["event", "amount", "other"])
        writer.writeheader()
        for entry in account.statement():
            kind = entry[0]
            if kind == "OPEN":
                continue
            if kind in ("DEPOSIT", "WITHDRAW"):
                _, amt = entry
                writer.writerow({"event": kind, "amount": amt, "other": ""})
            elif kind in ("TRANSFER_OUT", "TRANSFER_IN"):
                _, amt, other = entry
                writer.writerow({"event": kind, "amount": amt, "other": other})
            else:
                raise ValueError(f"Unknown ledger entry: {entry}")

def export_all_transactions_to_csv(accounts: Iterable[BankAccount], out_csv: str | Path) -> None:
    """
    Export combined transactions for all accounts
    (schema: owner,event,amount,other)
    """
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["owner", "event", "amount", "other"])
        writer.writeheader()
        for a in accounts:
            for entry in a.statement():
                kind = entry[0]
                if kind == "OPEN":
                    continue
                row = {"owner": a.owner, "event": kind, "amount": "", "other": ""}
                if kind in ("DEPOSIT", "WITHDRAW"):
                    _, amt = entry
                    row["amount"] = amt
                elif kind in ("TRANSFER_OUT", "TRANSFER_IN"):
                    _, amt, other = entry
                    row["amount"] = amt
                    row["other"] = other
                else:
                    raise ValueError(f"Unknown ledger entry: {entry}")
                writer.writerow(row)

def apply_transactions_from_csv(trans_csv: str | Path, accounts_by_owner: Dict[str, BankAccount]) -> None:
    """
    Apply transactions from CSV. Accepts flexible headers (case/space/BOM tolerant):
      owner, event, amount, other
    """
    auto_pairs: List[Tuple[str, float, str]] = []

    with _open_csv_text(trans_csv) as f:
        reader = _csv_reader_with_sniff(f)

        if not reader.fieldnames:
            raise ValueError("transactions.csv appears empty or has no header row.")

        norm_fields = [fn.strip().lower() for fn in reader.fieldnames]
        mapper = {orig: norm for orig, norm in zip(reader.fieldnames, norm_fields)}

        required = {"owner", "event", "amount", "other"}
        if not required.issubset(set(norm_fields)):
            raise ValueError(
                f"transactions.csv missing required headers {required}. Found: {norm_fields}"
            )

        rows = []
        for row in reader:
            # skip blank lines
            if row is None or all((v is None or str(v).strip() == "") for v in row.values()):
                continue
            nrow = {
                mapper[k]: (v.strip() if isinstance(v, str) else v)
                for k, v in row.items() if k is not None
            }
            rows.append(nrow)

    for row in rows:
        owner = row["owner"]
        event = row["event"].upper()
        amount = float(row["amount"]) if str(row["amount"]) != "" else 0.0
        other = row.get("other", "")

        if owner not in accounts_by_owner:
            raise KeyError(f"Unknown account owner: {owner}")

        acct = accounts_by_owner[owner]

        if event == "DEPOSIT":
            acct.deposit(amount)
        elif event == "WITHDRAW":
            acct.withdraw(amount)
        elif event == "TRANSFER_OUT":
            if not other or other not in accounts_by_owner:
                raise KeyError(f"TRANSFER_OUT needs valid 'other' account. Got: {other!r}")
            acct.transfer_to(accounts_by_owner[other], amount)
            auto_pairs.append((other, amount, owner))
        elif event == "TRANSFER_IN":
            if (owner, amount, other) in auto_pairs:
                continue
            if not other or other not in accounts_by_owner:
                raise KeyError(f"TRANSFER_IN needs valid 'other' account. Got: {other!r}")
            accounts_by_owner[other].transfer_to(acct, amount)
            auto_pairs.append((owner, amount, other))
        else:
            raise ValueError(f"Unknown event: {event}")

# -------------
# Tiny CLI (optional)
# -------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bank CSV I/O utility")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_apply = sub.add_parser("apply", help="Apply transactions to accounts")
    p_apply.add_argument("--accounts", required=True, help="Path to accounts.csv")
    p_apply.add_argument("--transactions", required=True, help="Path to transactions.csv")
    p_apply.add_argument("--out-balances", required=True, help="Where to write balances CSV")

    p_dump = sub.add_parser("dump-ledgers", help="Export all transactions after applying")
    p_dump.add_argument("--accounts", required=True)
    p_dump.add_argument("--transactions", required=True)
    p_dump.add_argument("--out-ledgers", required=True)

    args = parser.parse_args()

    if args.cmd == "apply":
        acc = load_accounts_from_csv(args.accounts)
        apply_transactions_from_csv(args.transactions, acc)
        export_accounts_to_csv(acc.values(), args.out_balances)
    elif args.cmd == "dump-ledgers":
        acc = load_accounts_from_csv(args.accounts)
        apply_transactions_from_csv(args.transactions, acc)
        export_all_transactions_to_csv(acc.values(), args.out_ledgers)
