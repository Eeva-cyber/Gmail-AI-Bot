from email.mime.text import MIMEText
import base64
from googleapiclient.errors import HttpError
from rich.panel import Panel
from rich.console import Console

from ..gmail_quickstart import authenticate_gmail

def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(service, user_id, message, console: Console):
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        success_message = f"Message sent successfully! Message Id: {sent_message['id']}"
        console.print(Panel(success_message, title="Email Sent"))
        return success_message
    except HttpError as error:
        error_message = f"An error occurred: {error}"
        console.print(error_message)
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred while sending email: {e}"
        console.print(error_message)
        return error_message
