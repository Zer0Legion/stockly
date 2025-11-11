import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown

from app.settings import Settings


class EmailService:
    def __init__(self):
        self.settings: Settings = Settings().get_settings()

    def send_email(self, to_email: str, subject: str, body: str):
        # Convert Markdown to HTML
        html_body = markdown.markdown(body)

        # Create the email message
        message_body = MIMEMultipart()
        message_body["From"] = self.settings.EMAIL_ADDRESS
        message_body["To"] = to_email
        message_body["Subject"] = subject
        message_body.attach(MIMEText(html_body, "html"))

        # Connect to the Gmail SMTP server
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()

        # Log in to the server
        server.login(self.settings.EMAIL_ADDRESS, self.settings.EMAIL_PASSWORD)

        # Send the email
        server.sendmail(self.settings.EMAIL_ADDRESS, to_email, message_body.as_string())

        # Close the connection
        server.quit()
