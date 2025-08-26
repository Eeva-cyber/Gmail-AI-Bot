import csv
import os
from dotenv import load_dotenv
from openai import OpenAI
from email_client import GmailClient
from rich import Console
from rich import Panel
from tools import available_tools

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

gmail = GmailClient()
console = Console()

# ----------------------
# Define available tools
# ----------------------
tools = [
    {
        "name": "generate_rejection_email",
        "description": "Generate a rejection email for a job applicant.",
        "parameters": {
            "type": "object",
            "properties": {
                "applicant_name": {
                    "type": "string", 
                    "description": "The name of the applicant."
                },
                "feedback": {
                    "type": "string", 
                    "description": "Feedback to include in the rejection email."
                }
            },
            "required": ["applicant_name", "feedback"]
        }
    }
]


# ----------------------
# Conversation memory
# ----------------------
messages = [
    {"role": "system", "content": "You are a helpful assistant. Always use the provided tools for calculations and weather queries. Do not answer directly."}
]


# ----------------------
# Run local tool
# ----------------------
def run_tool(function_name, **arguments):
    if function_name in local_tools:
        return local_tools[function_name](**arguments)
    return f"Unknown tool: {function_name}"


# ----------------------
# Chat with function calling
# ----------------------
def chat_with_functions(user_input: str) -> str:
    ## ask for user input here
    messages.append({"role": "user", "content": user_input})

    # First call to model
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        functions=tools,
        function_call="auto"
    )
    assistant_message = response.choices[0].message

    # Check if a function call is requested
    func_call = getattr(assistant_message, "function_call", [])
    if func_call:
        function_name = func_call.name
        arguments = json.loads(func_call.arguments)

        console.print(f"[bold yellow]Calling function:[/bold yellow] {function_name} with arguments {arguments}")
        try:
            result = run_tool(function_name, **arguments)
            console.print(f"[bold green]Tool result:[/bold green] {result}")
        except Exception as e:
            console.print(f"[bold red]Error calling function {function_name}:[/bold red] {e}")
            result = None

        # Send function result back to model for final response
        # Append assistant message first to keep the chain
        messages.append(assistant_message.model_dump())

        # The SDK handles function results via a "message from assistant with role 'assistant'"
        messages.append({
            "role": "function",
            "name": function_name,
            "content": str(result)
        })

        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        final_message = final_response.choices[0].message
        messages.append(final_message.model_dump())
        return final_message.content or "[bold red]No response from assistant[/bold red]"

    # If no function call, just return content
    messages.append(assistant_message.model_dump())
    return assistant_message.content or "[bold red]No response from assistant[/bold red]"

with open("rejected_interview.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        first_name = row["first_name"]
        last_name = row["last_name"]
        email = row["email"]
        feedback = row.get("Exec Comments", "").strip()

        if not feedback:
            print(f"⚠️ Skipping {first_name} {last_name} ({email}) — no feedback provided.")
            continue


        print(f"✏️ Generating rejection email for {first_name} {last_name}...")
        attempts = 0
        max_attempts = 10

        while attempts < max_attempts:
            body = generate_rejection_email(first_name, feedback)
            print("\n Preview email:\n")
            print(body)
            user_input = input("\nDo you want to sent this email? (y=yes / r= regenerate / s = skip) ").strip().lower()

            if user_input == "y":
                subject = "Application to DsCubed"
                gmail.send_email(
                    sender="recruitment@dscubed.org.au",
                    recipient=email,
                    subject=subject,
                    body=body
                )
                print(f"✅ Email sent to {first_name} {last_name}({email})\n")
                break

            elif user_input == "r":
                attempts += 1
                print("🔁 Regenerating...\n")
            elif user_input == "s":
                print(f"⏭️ Skipped {first_name} {last_name} ({email})\n")
                break
            else:
                print("❌ Invalid input. Please enter 'y', 'r', or 's'.")






# ----------------------
# Main loop
# ----------------------
def main():
    console.print(Panel("[bold green]Welcome to your AI chatbot! How can I help you today?[/bold green]", expand=False))

    while True:
        user_input = console.input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            console.print(Panel("[bold red]Goodbye![/bold red]", expand=False))
            break

        response = chat_with_functions(user_input)
        console.print(Panel(response, title="[bold green]Assistant[/bold green]", expand=False))

# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    main()