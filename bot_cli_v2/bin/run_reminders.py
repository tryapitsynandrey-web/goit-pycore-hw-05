#!/usr/bin/env python3
"""Невеликий скрипт-обгортка для експорту майбутніх днів народження або відсилання їх поштою.

Використання:
  bin/run_reminders.py --data-dir PATH --out reminders.csv [--days N] [--send-email]

Змінні оточення для SMTP (якщо --send-email):
  SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_TO
"""

import argparse
from pathlib import Path

from reminder import export_reminders, send_reminders_email


def main():
    p = argparse.ArgumentParser(prog="run_reminders")
    p.add_argument("--data-dir", required=True)
    p.add_argument("--out", required=False, default="reminders.csv")
    p.add_argument("--days", type=int, default=7)
    p.add_argument(
        "--send-email",
        action="store_true",
        help="Send reminders via SMTP (env vars required)",
    )
    args = p.parse_args()

    data_dir = Path(args.data_dir)
    out = Path(args.out)

    if args.send_email:
        # викличе виняток якщо змінні оточення SMTP не налаштовано
        result = send_reminders_email(data_dir, None, days=args.days)
        print(result)
    else:
        n = export_reminders(data_dir, out, days=args.days)
        print(f"Exported {n} reminders to {out}")


if __name__ == "__main__":
    main()
