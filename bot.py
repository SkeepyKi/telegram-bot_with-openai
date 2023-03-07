import os
from dotenv import load_dotenv, find_dotenv
import os
import re
import openai
import telebot
import requests
import datetime
import time
from bs4 import BeautifulSoup
from dnevnikru import Dnevnik
from pydub import AudioSegment
from ffmpeg import FFmpeg, Progress

load_dotenv(find_dotenv())
today = datetime.datetime.now()
today_string = today.strftime('%d/%m/%Y').replace("/", ".")
current_date = datetime.datetime.now() + datetime.timedelta(days=1)
current_date_string = current_date.strftime('%d/%m/%Y').replace("/", ".")
dn = Dnevnik(login=os.getenv("login"), password=os.getenv("password"))
openai.api_key = os.getenv("TOKEN_AI")
token = os.getenv("TOKEN")
bot = telebot.TeleBot(token)
print(today_string)


@bot.message_handler(func=lambda _: True)
def handle_message(message):
    general = message.chat.id
    def ne_pon():
        bot.reply_to(message, text='Ле брад не понял че сказал')
        bot.send_sticker(general, reply_to_message_id=message.message_id, sticker="CAACAgIAAxkBAAEH06tj83vHZ7LdlAPrVFGp016o-aFQcAACZgYAAhyS0gNzji83oMbdci4E")
    def pon():
        print("Не закрепил :(")
    try:
        response = openai.Moderation.create(
            input=message.text
        )
        output = response["results"][0]["flagged"]
        if output:
            bot.reply_to(message, text='Ле брад не сквернословь')
            bot.send_sticker(general, reply_to_message_id=message.message_id, sticker="CAACAgIAAxkBAAEHxStj7kbfmAVLWtplSQwVQfQDQHtc9AAC0AQAAhyS0gNOf6NUwIBZfi4E")
        else:
            if re.match(r'/gpt', message.text):
                try:
                    input = input = f"{message.text}\nPlease write answer on Russia language"
                    input = input.removeprefix('/gpt ')
                    print(input)
                    completion = openai.ChatCompletion.create( model="gpt-3.5-turbo", messages=[{"role": "user", "content": input}])
                    output = completion.choices[0].message
                    bot.reply_to(message, text=output.content)
                except:
                    ne_pon()
            elif re.match(r"/img", message.text):
                try:
                    response = openai.Image.create(
                        prompt=message.text,
                        n=1,
                        size="1024x1024"
                    )
                    image_url = response['data'][0]['url']
                    bot.send_photo(general, reply_to_message_id=message.message_id, photo=image_url)
                    print(message.text, message.chat.id, "  ---  ", image_url)
                except:
                    ne_pon()
            elif re.match(r"/code", message.text):
                try:
                    print(message.text)
                    response = openai.Completion.create(
                        model="code-davinci-002",
                        prompt=message.text,
                        temperature=0,
                        max_tokens=4000,
                        top_p=1.0,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                    )
                    bot.reply_to(message, text=response['choices'][0]['text'])
                    print(message.text, message.chat.id, "  ---  ", response['choices'][0]['text'])
                except:
                    ne_pon()
            elif re.match(r"/trn", message.text):
                try:
                    response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt="Translate to Russian language\n" + message.reply_to_message.text,
                        temperature=0.3,
                        max_tokens=2000,
                        top_p=1.0,
                        frequency_penalty=0.0,
                        presence_penalty=0.0
                    )
                    bot.reply_to(message, text=response['choices'][0]['text'])
                    print(message.text, message.chat.id, "  ---  ", response['choices'][0]['text'])
                except:
                    ne_pon()
    except:
        ne_pon()
    if re.match(r"/help", message.text):
        bot.reply_to(message, text="""
            
/gpt {текст} - генерация текста
/img {текст} - генерация картинки
/code {текст} - поиск ошибок в коде/генерация кода
/trn {ответ на сообщение} - перевод текста на русский
/wth - узнать погоду
/dze - узнать домашку
            """)
    elif re.match(r"/dze", message.text):
            try:
                homework = dn.homework(datefrom=current_date_string, days=0)
                homework2 = dn.homework(datefrom=today_string, days=0)
                put = homework
                put2 = homework2
                results = ['', '', '', '', '', '', '']
                results2 = ['', '', '', '', '', '', '']
                for i in range(7):
                    try:
                        if put["homework"][i] != "None":
                            output = put["homework"][i]
                            result = output[0] + " - " + output[1]
                            results[i] = result
                    except:
                        output = ["None", "None"]
                for i in range(7):
                    try:
                        if put2["homework"][i] != "None":
                            output = put2["homework"][i]
                            result2 = output[0] + " - " + output[1]
                            results2[i] = result2
                    except:
                        output = ["None", "None"]
                if results[0] == "":
                    bot.reply_to(message, text="Дебил завтра выходной")
                else:
                    results = f" На завтра: \n\n{results[0]}\n\n{results[1]}\n\n{results[2]}\n\n{results[3]}\n\n{results[4]}\n\n{results[5]}\n\n{results[6]}\n\n"
                    bot.reply_to(message, text=results)
                    msg_id = message.message_id + 1
                    bot.pin_chat_message(general, message_id=msg_id)
                if results2[0] == "":
                    bot.reply_to(message, text="Дебил сегодня выходной")
                else:
                    results2 = f"На сегодня: \n\n{results2[0]}\n\n{results2[1]}\n\n{results2[2]}\n\n{results2[3]}\n\n{results2[4]}\n\n{results2[5]}\n\n{results2[6]}\n"
                    bot.reply_to(message, text=results2)
                print(message.text, message.chat.id, "  ---  ", results)
                print(message.text, message.chat.id, "  ---  ", results2)
            except:
                ne_pon()
    elif re.match(r"/wth", message.text):
        try:
            url = "https://yandex.com.am/weather/details/10-day-weather?lat=54.584464&lon=73.638021&via=ms"
            response = requests.get(url, proxies=dict(http='socks5://yEog1h:dU8eAw@193.233.60.56:9641',
                                                      https='socks5://yEog1h:dU8eAw@193.233.60.56:9641'))
            bs = BeautifulSoup(response.text, "lxml")
            temp = bs.find_all('span', 'a11y-hidden')[0]
            temp2 = bs.find_all('span', 'a11y-hidden')[3]
            temp3 = bs.find_all('span', 'a11y-hidden')[6]
            temp4 = bs.find_all('span', 'a11y-hidden')[9]
            temp5 = bs.find_all('span', 'a11y-hidden')[12]
            output = f'''  
            
Таврическое
{temp.text}:
        
{temp2.text}
{temp3.text}
{temp4.text}
{temp5.text}
    '''
            bot.reply_to(message, text=output)
            print(message.text, message.chat.id, "  ---  ", output)
        except:
            ne_pon()



@bot.message_handler(content_types=['voice'])
def repeat_all_message(message):
    def ne_pon():
        bot.reply_to(message, text='Ле брад не понял че сказал')
        bot.send_sticker(message.chat.id, reply_to_message_id=message.message_id, sticker="CAACAgIAAxkBAAEH06tj83vHZ7LdlAPrVFGp016o-aFQcAACZgYAAhyS0gNzji83oMbdci4E")
    try:
        file_info = bot.get_file(message.voice.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))

        with open('voice.ogg','wb') as f:
            f.write(file.content)
        time.sleep(2)
        ffmpeg = (
            FFmpeg()
            .option("y")
            .input("voice.ogg")
            .output(
                "output.mp3",
                {"codec:v": "libx264"},
                vf="scale=1280:-1",
                preset="veryslow",
                crf=24,
            )
        )

        ffmpeg.execute()
        time.sleep(4)
        audio_file = open("output.mp3", "rb")
        transcript = openai.Audio.translate("whisper-1", audio_file)
        output = transcript.text
        output2 = output
        print(output)
        bot.reply_to(message, text=output)
        input = f"Please write answer on Russia language\n{output2}"
        print(input)
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": input}])
        output = completion.choices[0].message
        bot.reply_to(message, text=output.content)
    except:
        ne_pon()


bot.infinity_polling()