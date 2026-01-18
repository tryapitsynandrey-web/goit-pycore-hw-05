import csv
import os
import smtplib
import tempfile
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Optional

from core import AppService


def export_reminders(data_dir: Path | str, out_path: Path | str, days: int = 7) -> int:
    """Експортує майбутні дні народження у CSV файл. Повертає кількість експортованих рядків."""
    data_dir = Path(data_dir)
    out_path = Path(out_path)
    svc = AppService(data_dir)
    rows = svc.upcoming_birthdays(days=days)

    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["name", "phone", "birthday", "days_until", "notes"]
        )  # type: ignore[arg-type]
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "name": r.get("name", ""),
                    "phone": r.get("phone", ""),
                    "birthday": r.get("birthday", ""),
                    "days_until": r.get("days_until", ""),
                    "notes": r.get("notes", ""),
                }
            )

    return len(rows)


def send_reminders_email(
    data_dir: Path | str, smtp_settings: Optional[Dict[str, str]] = None, days: int = 7
) -> str:
    """Генерує CSV з майбутніми днями народження і надсилає його як вкладення електронною поштою.

    Ключі smtp_settings: server, port, username, password, from_addr, to_addrs (через кому).
    Якщо smtp_settings == None, читає налаштування з змінних оточення:
      SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_TO

    Повертає message-id або піднімає виняток при помилці.
    """
    data_dir = Path(data_dir)
    smtp = smtp_settings or {}
    if not smtp:
        smtp = {
            "server": os.environ.get("SMTP_SERVER"),
            "port": os.environ.get("SMTP_PORT"),
            "username": os.environ.get("SMTP_USER"),
            "password": os.environ.get("SMTP_PASS"),
            "from_addr": os.environ.get("SMTP_FROM"),
            "to_addrs": os.environ.get("SMTP_TO"),
        }

    required = ["server", "port", "from_addr", "to_addrs"]
    missing = [k for k in required if not smtp.get(k)]
    if missing:
        raise ValueError(f"Missing SMTP settings: {', '.join(missing)}")

    # створити тимчасовий CSV файл
    with tempfile.NamedTemporaryFile(
        prefix="birthdays_", suffix=".csv", delete=False
    ) as tf:
        out_path = Path(tf.name)
    try:
        # підготувати сервіс та експортувати CSV
        svc = AppService(data_dir)
        count = export_reminders(data_dir, out_path, days=days)

        # отримати рядки від сервісу
        rows = svc.upcoming_birthdays(days=days)

        msg = EmailMessage()
        msg["Subject"] = f"Upcoming birthdays: {count} in next {days} days"
        msg["From"] = smtp["from_addr"]
        msg["To"] = smtp["to_addrs"]

        # Текстова (plain) підсумкова частина листа
        plain = f"{count} upcoming birthdays in the next {days} days. See attached CSV or HTML table.\n"

        # Побудувати HTML за допомогою Jinja2 якщо доступно для кращого шаблону
        try:
            from jinja2 import Template

            tpl = Template("""
<html><body>
<p>{{ count }} upcoming birthdays in the next {{ days }} days.</p>
<table border=1 cellpadding=4 cellspacing=0>
  <thead><tr><th>Name</th><th>Phone</th><th>Birthday</th><th>Days Until</th><th>Notes</th></tr></thead>
  <tbody>
  {% for r in rows %}
    <tr>
      <td>{{ r.name }}</td>
      <td>{{ r.phone }}</td>
      <td>{{ r.birthday }}</td>
      <td>{{ r.days_until }}</td>
      <td>{{ r.notes }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>
</body></html>
""")

            # перетворити рядки на об'єкти для зручності у шаблоні
            class _R:
                def __init__(self, d):
                    self.name = d.get("name", "")
                    self.phone = d.get("phone", "")
                    self.birthday = d.get("birthday", "")
                    self.days_until = d.get("days_until", "")
                    self.notes = d.get("notes", "")

            html_table = tpl.render(count=count, days=days, rows=[_R(r) for r in rows])
        except Exception:
            html_rows = []
            for r in rows:
                name = r.get("name", "")
                phone = r.get("phone", "")
                bday = r.get("birthday", "")
                days_until = r.get("days_until", "")
                notes = r.get("notes", "")
                html_rows.append(
                    f"<tr><td>{name}</td><td>{phone}</td><td>{bday}</td><td>{days_until}</td><td>{notes}</td></tr>"
                )

            html_table = (
                "<html><body>"
                f"<p>{count} upcoming birthdays in the next {days} days.</p>"
                "<table border=1 cellpadding=4 cellspacing=0>"
                "<thead><tr><th>Name</th><th>Phone</th><th>Birthday</th><th>Days Until</th><th>Notes</th></tr></thead>"
                "<tbody>" + "\n".join(html_rows) + "</tbody></table></body></html>"
            )

        msg.set_content(plain)
        msg.add_alternative(html_table, subtype="html")

        # Додати CSV як вкладення
        with out_path.open("rb") as fh:
            data = fh.read()
        msg.add_attachment(data, maintype="text", subtype="csv", filename=out_path.name)

        server = smtp["server"]
        port = int(smtp["port"])
        username = smtp.get("username")
        password = smtp.get("password")
        if username and password:
            s = smtplib.SMTP(server, port, timeout=30)
            s.starttls()
            s.login(username, password)
        else:
            s = smtplib.SMTP(server, port, timeout=30)

        try:
            s.send_message(msg)
            s.quit()
        finally:
            pass

        return f"sent:{out_path.name}"
    finally:
        try:
            out_path.unlink()
        except Exception:
            pass
