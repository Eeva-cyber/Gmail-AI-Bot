from googleapiclient.errors import HttpError
import base64
from email import message_from_bytes
from rich.panel import Panel
from rich.console import Console

from ..gmail_quickstart import authenticate_gmail

def get_email(service, user_id, email_id, console: Console):
    if not email_id or not isinstance(email_id, str):
        error_message = "Error: Email ID is missing or invalid. Please provide a valid email ID."
        console.print(Panel(error_message, title="Error", style="red"))
        return error_message

    try:
        message = service.users().messages().get(userId=user_id, id=email_id, format='raw').execute()
        msg_bytes = base64.urlsafe_b64decode(message['raw'])
        msg = message_from_bytes(msg_bytes)
        subject = msg['subject']
        sender = msg['from']
        snippet = message['snippet']
        summary = f"Subject: {subject}\nFrom: {sender}\nSnippet: {snippet}"
        console.print(Panel(summary, title="Email Summary"))
        return summary
    except HttpError as error:
        error_message = f"An error occurred while fetching email: {error}"
        console.print(error_message)
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        console.print(error_message)
        return error_message
