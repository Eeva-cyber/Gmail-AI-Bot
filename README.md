# Gmail AI Bot

This bot allows you to interact with your Gmail account directly from the terminal using Python and the Gmail API.

## Setup Instructions

### 1. Enable Gmail API and Download `credentials.json`

1.  Go to the [Google Cloud Console](https://console.developers.google.com/).
2.  Create a new project or select an existing one.
3.  Enable the Gmail API for your project.
4.  Configure the OAuth Consent Screen (if you haven't already).
5.  Go to 'Credentials', click 'Create Credentials' -> 'OAuth client ID'.
6.  Select 'Desktop app' as the application type and create it.
7.  Download the `credentials.json` file.
8.  Place the downloaded `credentials.json` file in the **root directory** of this project (e.g., `C:\Users\User\AI_DSCubed\gmail-ai-bot\credentials.json`).

### 2. Activate Virtual Environment

Open your terminal in the project root directory (`C:\Users\User\AI_DSCubed\gmail-ai-bot\`) and activate your `uv` virtual environment:

```bash
.\venv\Scripts\activate
```

### 3. Install Dependencies

With your virtual environment activated, install the necessary Python libraries:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib rich
```

## Running the Bot

After completing the setup, you can run the bot from the project root directory:

```bash
python src/gmail_ai_bot/main.py
```

Follow the prompts in the terminal to interact with the bot. Available commands are `read`, `write`, `reply`, and `exit`.
