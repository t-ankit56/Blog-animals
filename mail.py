import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")


class Mail:
    def __init__(self):
        self.name = ""
        self.email = ""
        self.phone = ""
        self.msg = ""

    def send_mail(self):
        message = f"name: {self.name}\nemail: {self.email}\nPhone Number: {self.phone}\nMessage: {self.msg}"
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=EMAIL, password=PASSWORD)
            connection.sendmail(from_addr=EMAIL, to_addrs="t.ankit5691@gmail.com",
                                msg=f"Subject: Blog Response\n\n{message}")
