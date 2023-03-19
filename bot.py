# import library
import os
import cloudscraper
from dotenv import load_dotenv, find_dotenv
import os
import openai
import telebot
from telebot import types
import requests
import time
import json
from bs4 import BeautifulSoup

# your tokens
load_dotenv(find_dotenv("a.env")) # config of tokens
openai.api_key = os.getenv("TOKEN_AI")
token = os.getenv("TOKEN")
bot = telebot.TeleBot(token)

# stickers of Telegram
swear = "CAACAgIAAxkBAAEIDPpkCJcDLIQ6GQABkFnHOSZBbLtCIK4AAs4WAALpLuFLd0C2qVG6ir4uBA" 
dont = "CAACAgIAAxkBAAEH06tj83vHZ7LdlAPrVFGp016o-aFQcAACZgYAAhyS0gNzji83oMbdci4E"
ronaldu = "CAACAgIAAxkBAAEIKQFkEzHFXSYGgDZ5UyXfPDvVP9yprQACkxEAAj_8yEsIJ-TtlM4BTi8E"

# other 
config = "config.txt"
config_ru = "ru.txt"

def ne_pon(message): # for errors during bot operation
  general = message.chat.id
  bot.reply_to(message, text="My brother, I didn't understand what you said")
  bot.send_sticker(general, reply_to_message_id=message.message_id, sticker=dont)

def skverna(message): # for swear in message
  general = message.chat.id
  bot.reply_to(message, text="My brother don't swear")
  bot.send_sticker(general, reply_to_message_id=message.message_id, sticker=swear)

@bot.message_handler(commands=['gpt']) # generating text using openai
def gpt_input(message):
  try:
      response = openai.Moderation.create(input=message.text) # checking the adequacy of the request
      output = response["results"][0]["flagged"]
      if output:
        skverna(message)
      else:
        input = message.text
        input = input.removeprefix('/gpt ')
        print(input)
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": input}])
        output = completion.choices[0].message
        bot.reply_to(message, text=output.content)
  except:
    ne_pon(message)


@bot.message_handler(commands=['img']) # generating image using openai
def img_input(message):
  general = message.chat.id # Setting a variable to store chat_id
  try:
    response = openai.Moderation.create(input=message.text) # checking the adequacy of the request
    output = response["results"][0]["flagged"]
    if output:
      skverna(message)
    else:
      response = openai.Image.create(prompt=message.text, n=1, size="1024x1024")
      image_url = response['data'][0]['url']
      bot.send_photo(general, reply_to_message_id=message.message_id, photo=image_url)
  except:
    ne_pon(message)


@bot.message_handler(commands=['trn']) # we translate the text into any language using openai
def trn_input(message):
  try:
      response = openai.Moderation.create(input=message.text)
      output = response["results"][0]["flagged"]
      if output:
        skverna(message)
      else:
        input = message.text.removeprefix('/trn')
        if input == "": # setting the default value
          input = 'Русский' #Russian
        print(input)
        content = f"Translate to {input} language:\n{message.reply_to_message.text}"
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])
        output = completion.choices[0].message
        bot.reply_to(message, text=output.content)
  except:
    ne_pon(message)


@bot.message_handler(commands=['help']) # view the capabilities of the bot
def help(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	btn1 = types.KeyboardButton("Enable/Disable communication mode")
	markup.add(btn1)
	bot.reply_to(message, text=
""" 
/gpt {text} - text generation
/img {text} - image generation
/trn {ex: Russian} - text translation to any language
/wth {ex: Moscow} - find out the weather
/reg - Verification if you are on the list

Use /trn as a reply to a message.
""", reply_markup=markup)

@bot.message_handler(commands=['wth']) # we get the weather of any city
def wth(message):
  try:
    input = message.text.removeprefix("/wth ")
    url = f"https://yandex.com.am/weather/{input}/details/10-day-weather?via=ms"
    response = requests.get(url)
    bs = BeautifulSoup(response.text, "lxml")
    temp = bs.find_all('span', 'a11y-hidden')[0] # date
    temp2 = bs.find_all('span', 'a11y-hidden')[3] # morning
    temp3 = bs.find_all('span', 'a11y-hidden')[6] # day
    temp4 = bs.find_all('span', 'a11y-hidden')[9] # evening
    temp5 = bs.find_all('span', 'a11y-hidden')[12] # night
    output = f'\n{input}\n{temp.text}:\n\n{temp2.text}\n{temp3.text}\n{temp4.text}\n{temp5.text}'
    bot.reply_to(message, text=output)
  except:
      ne_pon(message)


@bot.message_handler(commands=['inf']) # check status of app / site
def inf(message):
    scraper = cloudscraper.create_scraper()
    url = "https://downdetector.com/status/" # url of the site that checks status of the app
    url += f"{message.text}/" # adding name app for url
    out = BeautifulSoup(scraper.get(url).text, "lxml")
    temp = out.find("div", "h2 entry-title").text
    bot.reply_to(message, text = temp)
    def ne_pon():
        print("no recent errors")
    try:
        temp2 = out.find('p', "text-danger").text
        bot.reply_to(message, text = temp2)
    except:
        ne_pon(message)

@bot.message_handler(commands=['reg']) # Registering a user in a dictionary (list); This occurs in the following way: user_id:status_mod_of_communication in config.txt
def reg(message):
    general = message.chat.id
    d2 = json.load(open(config))
    dic = {}
    dic = d2 | dic
    try:
        if f'{message.from_user.id}' in d2:
            bot.reply_to(message, "You are already on the list")
        else:
            bot.reply_to(message, "Adding to the list...")
            bot.send_sticker(general,
                            reply_to_message_id=message.message_id,
                            sticker=ronaldu)
            dic[message.from_user.id] = 0
            json.dump(dic, open(config, "w"))
            print(dic)
    except:
        ne_pon(message)


@bot.message_handler(commands=["change"])
def change(message):
    try:
        d2 = json.load(open(config))
        dic = {}
        dic = d2 | dic
        id = f'{message.from_user.id}'
        result = dic[id]
        if result == 0:
            dic[id] = 1
            json.dump(dic, open(config, "w"))
            bot.reply_to(message, "You can communicate")
        else:
            dic[id] = 0
            json.dump(dic, open(config, "w"))
            bot.reply_to(message, "Communication mode is turned off")
    except:
        bot.reply_to(message, "Perhaps you are not on the list?\nUse /reg")

@bot.message_handler(content_types=["infa"])
def inf_ru(message):
	try:
		app = message.text.removeprefix("/infa ")
		dct = json.load(open(config_ru))
		if app in dct:
			url = f"https://downdetector.br-analytics.ru/{dct[app]}"
		else:
			url = f"https://downdetector.br-analytics.ru/{app}"
		response = requests.get(url)
		bs = BeautifulSoup(response.text, "lxml")
		temp = bs.find('p', 'section_header-status_desc')
		bot.reply_to(message, temp.text)
	except:
		ne_pon(message)

@bot.message_handler(content_types=["text"])
def communication(message):
    try:
        if message.text == "Enable/Disable communication mode":
            change(message)
        else:
            d2 = json.load(open(config))
            dic = {}
            dic = d2 | dic
            id = f'{message.from_user.id}'
            result = dic[id]
            if result == 1:
                gpt_input(message)
    except:
        reg(message)


bot.infinity_polling() # launching an infinite bot
