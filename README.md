# Telegram bot with OpenAI GPT-3 functionality

This Telegram bot provides access to the OpenAI GPT-3 language model for generating text based on a prompt. It also has functionality for generating images based on a prompt, translating messages to any language using the language model, checking the status of an app or site, providing weather information for a given location, and enabling or disabling communication mode.

## Libraries used:

- os
- cloudscraper
- dotenv
- openai
- telebot
- requests
- json
- bs4

## Configuration tokens

- TOKEN_AI: OpenAI API key
- TOKEN: Telegram bot API key

## Commands available:
- /help: displays available commands and options
- /gpt {text}: generates text based on a given prompt
- /img {text}: generates an image based on a given prompt
- /trn {ex: Russian}: translates a text message to any language
- /reg: verifies if the user is on a list
- /wth {ex: Moscow}: provides weather information for a given location
- /inf {app_name}: checks the status of an app or site using Downdetector
- /infa {app_name}: checks the status of an app or site using a Russian version of Downdetector
- "/trn" as a reply to a message to translate it.

### Additional functionality:
- Enable/Disable communication mode option: allows users to enable or disable communication with OpenAI language model

### Stickers
- CAACAgIAAxkBAAEIDPpkCJcDLIQ6GQABkFnHOSZBbLtCIK4AAs4WAALpLuFLd0C2qVG6ir4uBA
- CAACAgIAAxkBAAEH06tj83vHZ7LdlAPrVFGp016o-aFQcAACZgYAAhyS0gNzji83oMbdci4E
- CAACAgIAAxkBAAEIKQFkEzHFXSYGgDZ5UyXfPDvVP9yprQACkxEAAj_8yEsIJ-TtlM4BTi8E

### How to run the bot
- Install all necessary libraries specified above (pip install -r requirements.txt -U)
- Type the token for your telegram bot API in TOKEN variable
- Type the token for OpenAI API in TOKEN_AI variable
- Run the final line of the code (bot.infinity_polling()) or deploy the bot to a platform such as Heroku.

I'm in telegram: https://t.me/Skeepy_Ki
This bot: https://t.me/GPTkir_bot
