import os
import cloudscraper
from dotenv import load_dotenv, find_dotenv
import os
import openai
import telebot
import requests
import time
from bs4 import BeautifulSoup
from ffmpeg import FFmpeg


load_dotenv(find_dotenv("a.env"))
openai.api_key = os.getenv("TOKEN_AI")
token = os.getenv("TOKEN")
bot = telebot.TeleBot(token)
swear = "CAACAgIAAxkBAAEIDPpkCJcDLIQ6GQABkFnHOSZBbLtCIK4AAs4WAALpLuFLd0C2qVG6ir4uBA" # sticker of Telegram
dont = "CAACAgIAAxkBAAEH06tj83vHZ7LdlAPrVFGp016o-aFQcAACZgYAAhyS0gNzji83oMbdci4E" # sticker of Telegram
output = 0
def ne_pon(message):
  general = message.chat.id
  bot.reply_to(message, text="My brother, I didn't understand what you said")
  bot.send_sticker(general, reply_to_message_id=message.message_id, sticker=dont)

def skverna(message):
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
        input = input = f"{message.text}\nPlease write answer on Russia language"
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
        content = f"Переведи на {input} язык:\n{message.reply_to_message.text}" # Translate to {input} language
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])
        output = completion.choices[0].message
        bot.reply_to(message, text=output.content)
  except:
    ne_pon(message)


@bot.message_handler(commands=['help']) # view the capabilities of the bot
def help(message):
  bot.reply_to(message, text="/gpt {текст} - генерация текста\n/img {текст} - генерация картинки\n/trn {пр: Русский} - перевод текста на любой язык\n/wth {пр: Moscow} - узнать погоду\n\n\n /trn использовать ответом на сообщение")
""" 
/gpt {text} - text generation
/img {text} - image generation
/trn {ex: Russian} - text translation to any language
/wth {ex: Moscow} - find out the weather

Use /trn as a reply to a message.
"""

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


@bot.message_handler(commands=['inf']) #
def inf(message):
  scraper = cloudscraper.create_scraper()
  url = "https://downdetector.com/status/" # url of the site that checks status of the app
  url += f"{message.text}/" #adding name app for url
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

@bot.message_handler(content_types=['voice']) # responds to any audio
def repeat_all_message(message):
  general = message.chat.id
  try:
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format( # download the audio .ogg from telegram servers
      token, file_info.file_path))
    time.sleep(2)
    with open('voice.ogg', 'wb') as f:
      f.write(file.content)
    ffmpeg = (FFmpeg().option("y").input("voice.ogg").output(  # .ogg to .mp3
      "output.mp3",
      {"codec:v": "libx264"},
      vf="scale=1280:-1",
      preset="veryslow",
      crf=24,
    ))

    ffmpeg.execute()
    time.sleep(2) # add if the file does not have time to process
    audio_file = open("output.mp3", "rb")
    transcript = openai.Audio.translate("whisper-1", audio_file)
    output = transcript.text
    output2 = output
    print(output)
    bot.reply_to(message, text=output)
    input = f"Please write answer on Russia language\n{output2}"
    print(input)
    response = openai.Moderation.create(input=input)
    output = response["results"][0]["flagged"]
    if output:
      skverna(message)
    else:
      completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": input}])
      output = completion.choices[0].message
      bot.reply_to(message, text=output.content)
  except:
    ne_pon(message)


bot.infinity_polling() # launching an infinite bot
