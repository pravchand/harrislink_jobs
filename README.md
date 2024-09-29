# harrislink_jobs

## How to Use

### Install Dependencies
First, install the `python-dotenv` package to manage `.env` files:

```bash
pip install python-dotenv
```

###  Create a .env file in your project root with the following content:
USERNAME=your_username

PASSWORD=your_password

SENDER_EMAIL=your_sender_email

SENDER_PASSWORD=your_app_password

RECEIVER_EMAIL=receiver1@example.com,receiver2@example.com

### Load the .env File
At the top of your script, load the .env file:

```bash
from dotenv import load_dotenv
load_dotenv()
```
