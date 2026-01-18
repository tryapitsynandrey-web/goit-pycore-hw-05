# 📇 Assistant CLI Address Book

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![CLI](https://img.shields.io/badge/Interface-CLI-informational.svg)
![JSON](https://img.shields.io/badge/Storage-JSON-success.svg)
![Logging](https://img.shields.io/badge/Logging-Enabled-yellow.svg)
![Status](https://img.shields.io/badge/Project-Portfolio--Ready-brightgreen.svg)

A **console-based assistant bot** for managing contacts.  
This project demonstrates **practical, production-oriented Python skills**, including CLI interaction, persistent storage, structured error handling, logging, and clean, maintainable architecture.

---

## 🚀 Features

- ➕ **Add new contacts**  
  Store contacts with validated and normalized phone numbers.

- ✏️ **Update existing phone numbers**  
  Safely modify contact data without silent overwrites.

- 🔍 **Search contacts**  
  Partial match search by name or phone number.

- 🗑️ **Remove contacts with confirmation**  
  Prevents accidental deletion via explicit confirmation.

- 🧾 **Rename contacts**  
  Rename a contact without changing its phone number.

- 📊 **View address book statistics**  
  Total contacts, unique phone numbers, last modification timestamp.

- 📋 **Clean terminal output**  
  Contacts and statistics are rendered as readable tables and boxes.

- 💾 **Automatic persistence (JSON)**  
  All changes are saved automatically after each modifying command.

- 🔄 **One-time migration support**  
  Legacy `contacts.txt` is automatically migrated to `contacts.json`.

- 🧠 **Robust input error handling**  
  The application never crashes on invalid user input.

- 📝 **Production-style logging**  
  All important actions are logged for traceability.

---

## 🧩 Available Commands

### 🔹 Basic Commands

- `hello`  
  Display a greeting message.

- `help`  
  Show the help screen with all available commands.

- `close` / `exit`  
  Exit the application gracefully.

### 🔹 Contact Management

- `add <name> <phone>`  
  Add a new contact.

- `change <name> <phone>`  
  Update an existing contact’s phone number.

- `phone <name>`  
  Display information for a specific contact.

- `all`  
  Show all saved contacts in a formatted table.

- `remove <name>`  
  Remove a contact (requires confirmation).

- `delete <name>`  
  Alias for `remove`.

- `rename <old> <new>`  
  Rename a contact without changing the phone number.

- `search <query>`  
  Search contacts by name or phone (partial match).

- `stats`  
  Display address book statistics.

---

## 📞 Phone Normalization

All phone numbers are stored in a **single, consistent format**:

- Spaces, brackets, and dashes are removed  
- `+` is allowed only at the beginning  
- `00XXXXXXXX` is converted to `+XXXXXXXX`  
- Length validation: **7–15 digits** (E.164 standard)

This guarantees clean data and prevents ambiguous duplicates.

---

## 🗂️ Project Structure

bot_cli_v2/
├── main_bot_cli_v3.py      # Application entry point (CLI logic)
├── address_book.py         # AddressBook class (domain logic)
├── storage.py              # Persistence and migration layer
├── utils.py                # Normalization & formatting helpers
├── ux_messages.py          # All UX messages and text
├── logger_setup.py         # Logging configuration
├── contacts.json           # Persistent contacts storage
├── logfile.log             # Application logs
├── requirements.txt
└── README.md

---

## 💾 Data Persistence

- Contacts are stored in `contacts.json`
- Saving is **atomic** (temporary file + replace)
- Data persists between application runs
- Legacy `contacts.txt` is migrated automatically (once)

---

## 🧠 Architecture Highlights

- **AddressBook** encapsulates all domain logic  
- **storage.py** provides a clean persistence abstraction  
- **utils.py** follows the Single Responsibility Principle  
- **ux_messages.py** cleanly separates UX from business logic  
- **input_error decorator** guarantees CLI stability  
- Minimal, readable, and production-oriented design

---

## 📝 Logging

All important actions are logged to `logfile.log`:

- Application start and exit  
- Executed commands  
- Input and validation errors  
- Data persistence events  

**Log format:**

YYYY-MM-DD HH:MM:SS | LEVEL | message

---

## ▶️ How to Run

python3 main_bot_cli_v3.py

### Optional: Virtual Environment

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

---

## 🛠️ Quick Usage Examples

CLI examples (quoted names supported):

- Add a contact:

  python3 main_bot_cli_v3.py
  add "John Doe" "+380501234567"

- Change phone:

  change "John Doe" "+380501234568"

- Show a contact's phone:

  phone "John Doe"

- Export to CSV:

  export backup.csv

- Import from CSV (transactional undo):

  import backup.csv

  # The import is recorded as a single operation for undo.

Command-line flags:

- `--data-dir PATH` — change where `contacts.json` and logs live.
- `--no-backups` — disable automatic JSON backups.
- `--allow-duplicates` — allow duplicate phone numbers.
- Auto-help: after 6 consecutive empty inputs or 6 invalid commands the `help` menu is shown automatically (configurable via `settings.py`).

## 🔗 HTTP API (optional)

If you run the optional FastAPI server (`run_api.py`), a simple HTTP API is available.

Example (create contact):

curl -X POST "http://127.0.0.1:8000/contacts" -H "Content-Type: application/json" -d '{"name":"Alice","phone":"+15551234567"}'

Example (fuzzy search):

curl "http://127.0.0.1:8000/fsearch?q=Al"

Birthdays API:

- List upcoming birthdays for next 7 days (default):

  curl "http://127.0.0.1:8000/birthdays"

- List upcoming birthdays next N days:

  curl "http://127.0.0.1:8000/birthdays?days=30"


## 🎯 Project Purpose

This project was built as:

- A **high-quality example** of a Python CLI application  
- A demonstration of **clean code and modular architecture**  
- A **portfolio-ready project** for GitHub, CV, and technical interviews  

---

## 🧠 Future Improvements

- Unit tests (pytest)
- Support for email and tags
- CSV import/export
- Command autocomplete
- CLI interface via `argparse` or `cmd`

## ⏰ Reminders & Scheduling

You can export upcoming birthdays (default next 7 days) and schedule it using cron.

Quick one-liner (cron):

```bash
# nightly at 01:00
0 1 * * * python3 -c "from reminder import export_reminders; export_reminders('/path/to/project', '/path/to/reminders.csv', days=7)"
```

Or use the provided runner script:

```bash
# export to CSV
bin/run_reminders.py --data-dir /path/to/project --out /tmp/reminders.csv --days 7

# send via SMTP (requires environment variables)
bin/run_reminders.py --data-dir /path/to/project --send-email --days 7
```

SMTP environment variables used when sending email:

- `SMTP_SERVER` (e.g. smtp.gmail.com)
- `SMTP_PORT` (e.g. 587)
- `SMTP_USER`
- `SMTP_PASS`
- `SMTP_FROM` (from address)
- `SMTP_TO` (comma-separated recipients)

Note: storing SMTP credentials in environment variables is simple but not the most secure option; consider a secrets manager for production.

### systemd example

If you use `systemd` you can run the reminder nightly with a unit + timer. Example files (place under `/etc/systemd/system/`):

- `/etc/systemd/system/bot-reminders.service`

```
[Unit]
Description=Export AddressBook upcoming birthdays

[Service]
Type=oneshot
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/env python3 bin/run_reminders.py --data-dir /path/to/project --out /var/opt/reminders.csv --days 7
```

- `/etc/systemd/system/bot-reminders.timer`

```
[Unit]
Description=Run bot reminders daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now bot-reminders.timer
```

