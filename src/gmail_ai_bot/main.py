from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Prompt

from .ai_service import AIService

def main():
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )

    ai_service = AIService()

    layout["header"].update(Panel("Gmail AI Bot", title="Header"))
    layout["footer"].update(Panel("Type 'exit' to quit", title="Footer"))

    while True:
        ai_service.console.print(layout)
        user_input = Prompt.ask("Enter your command")

        if user_input.lower() == 'exit':
            ai_service.console.print("Exiting bot. Goodbye!")
            break
        
        ai_service.chat_with_openai(user_input)

if __name__ == "__main__":
    main()
