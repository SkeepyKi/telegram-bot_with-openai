# import necessary libraries
import os
import cloudscraper    # for bypassing website's security measures
from dotenv import load_dotenv, find_dotenv    # for loading environment variables
import openai    # for using GPT-3 language model
import telebot    # for creating Telegram bot
from telebot import types    # for creating custom keyboard
import requests    # for making HTTP requests
import json    # for working with JSON data
from bs4 import BeautifulSoup    # for parsing HTML and XML documents

# Load configuration tokens
load_dotenv(find_dotenv("a.env")) # Look for environment variables in .env file
openai.api_key = os.getenv("TOKEN_AI") # Set OpenAI API key using the environment variable
token = os.getenv("TOKEN") # Set Telegram Bot API key using the environment variable

# Connect to Telegram Bot API using provided token
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

@bot.message_handler(commands=['gpt']) # defining the /gpt command
def gpt_input(message):
  try: # trying to execute the code
      response = openai.Moderation.create(input=message.text) # sending a request to check the adequacy of the message
      output = response["results"][0]["flagged"]
      if output: # if the message is inappropriate, invoking the skverna() function
        skverna(message)
      else:
        input = message.text
        input = input.removeprefix('/gpt ') # removing the command from the message
        print(input) # printing the message to console for debugging
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": input}]) # launching the OpenAI model to generate a response to the message
        output = completion.choices[0].message # getting the response to the message
        bot.reply_to(message, text=output.content) # sending the received response to the user
  except: # if an error occurs, invoking the ne_pon() function
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


@bot.message_handler(commands=['trn'])
def trn_input(message):
  try:
    # check if the input message violates OpenAI's content policy
    response = openai.Moderation.create(input=message.text)
    output = response["results"][0]["flagged"]
    if output:
      skverna(message) # if it contains inappropriate content, perform a specific action
    else:
      # extract the language to translate to from the user's input
      input_text = message.text.removeprefix('/trn').strip() # remove the command and whitespace
      if not input_text: # if no language is provided, set a default value
        input_text = 'Russian'
      print(input_text)
      # construct the prompt for OpenAI's GPT-3 language model
      content = f"Translate to {input_text} language:\n{message.reply_to_message.text}"
      # use the language model to generate the translation
      completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])
      # extract the translation from the response and send it to the user
      output_text = completion.choices[0].message.content # access the content property
      bot.reply_to(message, text=output_text)
  except:
    ne_pon(message) # if there's an error, perform a specific action


@bot.message_handler(commands=['help']) 
def help(message):
  # Creating a custom keyboard markup to show the available options
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = types.KeyboardButton("Enable/Disable communication mode")
  markup.add(btn1)
  # Using the bot's 'reply_to' method to send a text message with the available options and the custom keyboard markup
  bot.reply_to(message, text=
""" 
/gpt {text} - generates text based on a given prompt
/img {text} - generates an image based on a given prompt
/trn {ex: Russian} - translates a text message to any language
/wth {ex: Moscow} - provides weather information for a given location
/reg - verifies if the user is on a list

Use /trn as a reply to a message to translate it.

Please use the custom keyboard to access the 'Enable/Disable communication mode' option.
""", reply_markup=markup)

@bot.message_handler(commands=['wth'])
def wth(message):
  try:
    # Retrieve input from user
    input = message.text.removeprefix("/wth ")
    # Create URL to fetch weather data of input city
    url = f"https://yandex.com.am/weather/{input}/details/10-day-weather?via=ms"
    # Send a GET request to the URL and retrieve the response
    response = requests.get(url)
    # Create a Beautiful Soup object to parse the HTML content of the response
    bs = BeautifulSoup(response.text, "lxml")
    # Find all the span elements with class 'a11y-hidden' which contain weather data
    temp_list = bs.find_all('span', 'a11y-hidden')
    # Extract the required data from the list
    temp = temp_list[0] # date
    temp2 = temp_list[3] # morning temperature
    temp3 = temp_list[6] # day temperature
    temp4 = temp_list[9] # evening temperature
    temp5 = temp_list[12] # night temperature
    # Create output string with retrieved weather data
    output = f'\n{input}\n{temp.text}:\n\n{temp2.text}\n{temp3.text}\n{temp4.text}\n{temp5.text}'
    # Reply to user with the output string
    bot.reply_to(message, text=output)
  except:
      # If an error occurs, call a ne_pon function to notify the user
      ne_pon(message)


# This function handles the /inf command, which checks the status of an app or site
@bot.message_handler(commands=['inf'])
def inf(message):
    # First, we create a scraper object
    scraper = cloudscraper.create_scraper()
    # We construct the URL of the site that checks the status of the app or site we want to check
    url = "https://downdetector.com/status/"
    url += f"{message.text}/" # Adding the name of the app or site to the URL
    # We use the scraper to retrieve the page and parse it with BeautifulSoup
    out = BeautifulSoup(scraper.get(url).text, "lxml")
    # We extract the overall status message of the app or site and send it as a reply
    temp = out.find("div", "h2 entry-title").text
    bot.reply_to(message, text = temp)
    # We define a function that will be used to report that there are no recent errors
    def no_recent_errors():
        print("no recent errors")
    # Next, we check if there are any recent errors reported for the app or site
    try:
        temp2 = out.find('p', "text-danger").text # If there are, we extract the message and send it as a reply
        bot.reply_to(message, text = temp2)
    except:
        no_recent_errors(message) # If there are none, we call the no_recent_errors function.

# Registering a user in a dictionary (list) when "/reg" command is used
@bot.message_handler(commands=['reg'])
def reg(message):
    general = message.chat.id # get chat ID where the message was sent 
    d2 = json.load(open(config)) # load existing dictionary from a config file
    dic = {} # create a new dictionary object
    dic = d2 | dic # merge the two dictionaries
    try:
        if f'{message.from_user.id}' in d2: # check if user is already in the dictionary
            bot.reply_to(message, "You are already on the list") # if user is already in the dictionary, send a message to indicate that
        else:
            bot.reply_to(message, "Adding to the list...") # if user is not in the dictionary, send a message to indicate that a process of adding them to the dictionary has started
            bot.send_sticker(general, # send a sticker as a reply to the user's message
                            reply_to_message_id=message.message_id,
                            sticker=ronaldu)
            dic[message.from_user.id] = 0 # add user to the dictionary with a value of 0
            json.dump(dic, open(config, "w")) # update the contents of the config file with the modified dictionary
            print(dic) # print the dictionary for debugging purpose
    except:
        ne_pon(message) # if an error occurs, call the "ne_pon" function to handle it.


@bot.message_handler(commands=["change"])
def change(message):
    try:
        # Loading data from the config file and creating a dictionary
        d2 = json.load(open(config))
        dic = {}
        
        # Merging the two dictionaries into one
        dic = d2 | dic
        
        # Getting the user id
        id = f'{message.from_user.id}'
        
        # Checking the communication mode status for the user
        result = dic[id]
        
        # Changing the communication mode status for the user and saving it in the dictionary
        if result == 0:
            dic[id] = 1
            json.dump(dic, open(config, "w"))
            bot.reply_to(message, "You can communicate")
        else:
            dic[id] = 0
            json.dump(dic, open(config, "w"))
            bot.reply_to(message, "Communication mode is turned off")
    
    # Handling exceptions and prompting the user to register if not on the list
    except:
        bot.reply_to(message, "Perhaps you are not on the list?\nUse /reg")

@bot.message_handler(commands=["infa"])
def inf_ru(message):
  try:
    # Removing the '/infa ' prefix from the message text
    app = message.text.removeprefix("/infa ")
    # Loading a dictionary from a json file
    dct = json.load(open(config_ru))
    # If the app is in the dictionary, use the corresponding url
    if app in dct:
      url = f"https://downdetector.br-analytics.ru/{dct[app]}"
    # Otherwise, use the app as the url
    else:
      url = f"https://downdetector.br-analytics.ru/{app}"
    # Sending a GET request to the url and getting the response
    response = requests.get(url)
    # Parsing the HTML response with BeautifulSoup
    bs = BeautifulSoup(response.text, "lxml")
    # Finding the paragraph element with class 'section_header-status_desc'
    temp = bs.find('p', 'section_header-status_desc')
    # Replying to the user with the text content of the element
    bot.reply_to(message, temp.text)
  except:
    # Handling the case where an exception occurs
    ne_pon(message)

# This function handles incoming text messages
@bot.message_handler(content_types=["text"])
def communication(message):
    try:
        # Check if the user is trying to change communication mode
        if message.text == "Enable/Disable communication mode":
            change(message)
        # Otherwise, check if the user has communication mode enabled and proceed with GPT input
        else:
            # Load the configuration file containing user settings
            d2 = json.load(open(config))
            dic = {}
            dic = d2 | dic
            id = f'{message.from_user.id}'
            result = dic[id]
            # If communication mode is enabled for the user, proceed with GPT input
            if result == 1:
                gpt_input(message)
    except:
        # If the user is not registered yet, prompt them to register
        reg(message)


bot.infinity_polling() # launching an infinite bot