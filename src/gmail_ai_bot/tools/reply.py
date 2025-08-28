from email.mime.text import MIMEText
import base64
from email import message_from_bytes
from googleapiclient.errors import HttpError
from rich.panel import Panel
from rich.console import Console

from ..gmail_quickstart import authenticate_gmail
from .write import send_email, create_message

def send_reply(service, user_id, original_email_id, reply_text, console: Console):
    try:
        # Get the original message
        message = service.users().messages().get(userId=user_id, id=original_email_id, format='raw').execute()
        msg_bytes = base64.urlsafe_b64decode(message['raw'])
        msg = message_from_bytes(msg_bytes)

        original_subject = msg['subject']
        original_from = msg['from']
        original_message_id = msg['Message-ID']

        # Extract recipient email from the 'From' header
        # This is a simplified extraction and might need more robust parsing for complex email addresses
        to_address = original_from.split('<')[-1].replace('>', '')

        # Create reply message
        reply_subject = f"Re: {original_subject}"
        reply_message = MIMEText(reply_text)
        reply_message['to'] = to_address
        reply_message['subject'] = reply_subject
        reply_message['In-Reply-To'] = original_message_id
        reply_message['References'] = original_message_id

        encoded_message = {'raw': base64.urlsafe_b64encode(reply_message.as_bytes()).decode()}

        send_email(service, user_id, encoded_message, console)
        console.print(Panel(f"Reply sent successfully to {to_address}!", title="Email Reply Sent"))
        return "Reply initiated successfully."

    except HttpError as error:
        console.print(f"An error occurred: {error}")
        return f"Error sending reply: {error}"
    except Exception as e:
        error_message = f"An unexpected error occurred while sending reply: {e}"
        console.print(error_message)
        return error_message
