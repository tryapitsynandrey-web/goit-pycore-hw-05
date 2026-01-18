from datetime import date, timedelta


class FakeSMTP:
    last_message = None

    def __init__(self, server, port, timeout=30):
        self.server = server
        self.port = port
        self.timeout = timeout
        self._closed = False

    def starttls(self):
        return True

    def login(self, user, password):
        self.user = user
        self.password = password

    def send_message(self, msg):
        FakeSMTP.last_message = msg

    def quit(self):
        self._closed = True


def test_send_reminders_email_monkeypatched_smtp(tmp_path, monkeypatch):
    # створити директорію даних з контактом, у якого завтра день народження
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    from core import AppService

    svc = AppService(data_dir)
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    svc.add("Sam", "+380501230100", birthday=tomorrow, notes="Test")

    # замокати smtplib.SMTP
    import smtplib

    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)

    smtp_settings = {
        "server": "localhost",
        "port": "25",
        "username": "",
        "password": "",
        "from_addr": "from@example.com",
        "to_addrs": "to@example.com",
    }

    from reminder import send_reminders_email

    res = send_reminders_email(data_dir, smtp_settings=smtp_settings, days=7)
    assert res.startswith("sent:")

    # інспектувати останнє повідомлення
    msg = FakeSMTP.last_message
    assert msg is not None
    # тема містить 'Upcoming birthdays'
    assert "Upcoming birthdays" in msg["Subject"]

    # має бути HTML-альтернатива
    html_part = msg.get_body(preferencelist=("html",))
    assert html_part is not None
    assert "<table" in html_part.get_content()

    # має бути вкладення CSV
    attachments = list(msg.iter_attachments())
    assert len(attachments) == 1
    filename = attachments[0].get_filename()
    assert filename.endswith(".csv")
