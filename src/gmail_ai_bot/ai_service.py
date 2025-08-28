from rich.console import Console
from rich.panel import Panel
import openai
import json

from .gmail_quickstart import authenticate_gmail
from .tools.read import get_email
from .tools.write import create_message, send_email
from .tools.reply import send_reply
from .tools.list_emails import list_recent_emails

# Define the tools available to the AI
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_emails",
            "description": "Lists recent emails from the user's inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "The maximum number of emails to list. Defaults to 10."
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_email",
            "description": "Reads and summarizes a specific email given its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "The ID of the email to read."
                    }
                },
                "required": ["email_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_email",
            "description": "Composes and sends a new email to a recipient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "The recipient's email address."
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject of the email."
                    },
                    "body_instruction": {
                        "type": "string",
                        "description": "Instructions for generating the body content of the email."
                    }
                },
                "required": ["to", "subject", "body_instruction"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reply_email",
            "description": "Replies to a specific email with a given instruction for the reply content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "original_email_id": {
                        "type": "string",
                        "description": "The ID of the original email to reply to."
                    },
                    "reply_instruction": {
                        "type": "string",
                        "description": "Instructions for generating the reply text."
                    }
                },
                "required": ["original_email_id", "reply_instruction"],
            },
        },
    },
]


class AIService:
    def __init__(self):
        self.service = authenticate_gmail()
        self.user_id = 'me'
        self.console = Console()
        self.client = openai.OpenAI()
        self.messages = []

    def read_email(self, email_id):
        return get_email(self.service, self.user_id, email_id, self.console)

    def write_email(self, to, subject, body_instruction):
        generated_body = self._generate_email_content(body_instruction)
        message = create_message(to, subject, generated_body)
        return send_email(self.service, self.user_id, message, self.console)

    def reply_email(self, original_email_id, reply_instruction):
        # Fetch original email content to use as context for reply generation
        try:
            original_message = self.service.users().messages().get(userId=self.user_id, id=original_email_id, format='full').execute()
            # Extract sender and subject for better context
            headers = original_message['payload']['headers']
            original_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            original_from = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            
            # Decode the email body (this can be complex, just getting snippet for simplicity)
            snippet = original_message.get('snippet', 'No snippet available.')
            context = f"Original Email Subject: {original_subject}\nOriginal Email From: {original_from}\nOriginal Email Snippet: {snippet}"

        except Exception as e:
            self.console.print(Panel(f"Could not fetch original email for context: {e}", title="Warning", style="yellow"))
            context = ""

        generated_reply_text = self._generate_email_content(reply_instruction, context)
        return send_reply(self.service, self.user_id, original_email_id, generated_reply_text, self.console)

    def list_emails(self):
        return list_recent_emails(self.service, self.user_id, self.console)

    def chat_with_openai(self, user_message):
        self.messages.append({"role": "user", "content": user_message})
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            tools=tools,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
        self.messages.append(response_message)

        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            tool_output = None
            try:
                if function_name == "list_emails":
                    tool_output = self.list_emails()
                elif function_name == "read_email":
                    tool_output = self.read_email(function_args.get("email_id"))
                elif function_name == "write_email":
                    tool_output = self.write_email(function_args.get("to"), function_args.get("subject"), function_args.get("body_instruction"))
                elif function_name == "reply_email":
                    tool_output = self.reply_email(function_args.get("original_email_id"), function_args.get("reply_instruction"))
                else:
                    tool_output = f"Unknown tool: {function_name}"
                    self.console.print(Panel(tool_output, title="Error", style="red"))
            except Exception as e:
                tool_output = f"Error executing tool {function_name}: {e}"
                self.console.print(Panel(tool_output, title="Error", style="red"))
            
            self.messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": tool_output,
                }
            )
            # Make a second call to OpenAI to get its response after the tool execution
            second_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
            )
            self.messages.append(second_response.choices[0].message)
            self.console.print(Panel(second_response.choices[0].message.content, title="AI Response"))
        else:
            self.console.print(Panel(response_message.content, title="AI Response"))

    def _generate_email_content(self, instruction, context=""):
        prompt = (
            f"Given the following context and instruction, generate an email body:\n"
            f"Context: {context}\nInstruction: {instruction}\n\nEmail Body:"
            "Sign off as 'DsCubed Recruitment Team'. Please structure the email as a properly formatted email in HTML and remove the HTML tag."
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that drafts professional and polite emails based on user instructions."}, # system message for context
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
