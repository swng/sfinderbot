# **sfinderbot**

sfinder discord bot that computes various commands relevant to modern tetris research, mainly using [knewjade's sfinder tool](https://github.com/knewjade/solution-finder) (an executable .jar is included in this project).

*Created by cringemoment, epic, swng/kzl.*

## **Prerequisites**

1. Create a `.env` file in the project root directory with the following content:
   ```plaintext
   bot_token=DISCORD_TOKEN
   logging_webhook=webhooklink
   error_webhook=webhooklink
   edp_webhook=webhooklink
   ```

2. Install the required Python dependencies:
   ```bash
   pip install discord bs4 Pillow py-fumen-py py-fumen-util requests matplotlib python-dotenv
   ```

---

## **How to Run**

1. Run the project with:
   ```bash
   python main.py
   ```

2. To run the program in the background, use:
   ```bash
   nohup python3 main.py -u &
   ```

   You may also wish to use a variety of process managers instead.

---

## **Usage**

The bot has a variety of sfinder commands and more. You can get started with >help
