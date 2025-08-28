from googleapiclient.errors import HttpError
from rich.panel import Panel
from rich.console import Console

def list_recent_emails(service, user_id, console: Console, max_results=10):
    try:
        results = service.users().messages().list(userId=user_id, maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            console.print(Panel("No messages found.", title="Recent Emails"))
            return "No messages found."

        email_list_summary = "Recent emails:\n"
        console.print(Panel("Recent emails:", title="Recent Emails"))
        for msg in messages:
            msg_data = service.users().messages().get(userId=user_id, id=msg['id'], format='metadata', metadataHeaders=['From', 'Subject']).execute()
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            email_info = f"From: {sender} | Subject: {subject} | ID: {msg['id']}"
            console.print(email_info)
            email_list_summary += f"{email_info}\n"
        return email_list_summary

    except HttpError as error:
        error_message = f"An error occurred: {error}"
        console.print(error_message)
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred while listing emails: {e}"
        console.print(error_message)
        return error_message
