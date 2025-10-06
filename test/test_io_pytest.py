import csv
from pathlib import Path
from src.io_csv import (
    load_accounts_from_csv,
    export_accounts_to_csv,
    export_all_transactions_to_csv,
    apply_transactions_from_csv,
)

def test_accounts_roundtrip(tmp_path: Path):
    acc_csv = tmp_path / "accounts.csv"
    acc_csv.write_text("owner,opening_balance\nAlice,100\nBob,50\n", encoding="utf-8")

    accs = load_accounts_from_csv(acc_csv)
    assert set(accs.keys()) == {"Alice", "Bob"}
    assert accs["Alice"].balance == 100
    assert accs["Bob"].balance == 50

    out_csv = tmp_path / "balances.csv"
    export_accounts_to_csv(accs.values(), out_csv)
    rows = list(csv.DictReader(out_csv.open(encoding="utf-8")))
    assert {r["owner"] for r in rows} == {"Alice", "Bob"}
    # values formatted to 2 decimals
    assert all("balance" in r for r in rows)

def test_transactions_apply_and_export(tmp_path: Path):
    acc_csv = tmp_path / "accounts.csv"
    acc_csv.write_text("owner,opening_balance\nAlice,100\nBob,50\n", encoding="utf-8")

    tx_csv = tmp_path / "transactions.csv"
    tx_csv.write_text(
        "owner,event,amount,other\n"
        "Alice,DEPOSIT,20,\n"
        "Alice,WITHDRAW,10,\n"
        "Alice,TRANSFER_OUT,40,Bob\n",
        encoding="utf-8",
    )

    accs = load_accounts_from_csv(acc_csv)
    apply_transactions_from_csv(tx_csv, accs)

    assert accs["Alice"].balance == 70   # 100 +20 -10 -40
    assert accs["Bob"].balance == 90     # 50 +40

    all_tx = tmp_path / "all_tx.csv"
    export_all_transactions_to_csv(accs.values(), all_tx)
    rows = list(csv.DictReader(all_tx.open(encoding="utf-8")))
    kinds = {r["event"] for r in rows}
    assert "TRANSFER_OUT" in kinds and "TRANSFER_IN" in kinds
