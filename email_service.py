import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def send(self, to_email: str, subject: str, content: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.user
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(content, "plain"))

            with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error("Email error: %s", e)
            return False