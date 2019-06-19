import telebot
import requests
import urllib
from telebot.types import Message
from telebot import apihelper, types
from bs4 import BeautifulSoup
import random
import shutil
import numpy as np

TOKEN = '841260700:AAH1L11T4MLylzBCSc8z0Zc640Bb8upihpA'
PROXY = 'socks5://5.135.58.123:61537'

apihelper.proxy = {'https': PROXY}
bot = telebot.TeleBot(TOKEN)
url = ''
count_pages = 20


def pars_weather_page(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page)
    divs = soup.find_all("div", {'class': 'fact card card_size_big'})
    weather_list = []

    for li in divs:
        weather = []
        link_text = li.find('a')
        temp = link_text.find('span', {'class': 'temp__value'}).text
        # img = link_text.find('img', {'class': 'icon icon_color_light icon_size_48 icon_thumb_skc-d fact__icon'}).get(
        #     'src')
        # img = "https:" + img
        temp_feelings = link_text.find("div", {'class': 'link__feelings fact__feelings'})
        temp_fil = temp_feelings.find('span', {'class': 'temp__value'}).text
        day_anchor = temp_feelings.find('div', {'class': 'link__condition day-anchor i-bem'}).text
        weather.append(temp)
        # weather.append(img)
        weather.append(day_anchor)
        weather.append(temp_fil)
        weather_list.append(weather)
        print(temp)
        # print(img)
        print(day_anchor)
        print(temp_fil)
    return weather_list

# pars_weather_page('https://yandex.ru/pogoda/moscow/')

def pars_movi_page(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page)
    lis = soup.find_all("li", {'class': 'results-item-wrap'})
    movi_list = []

    for li in lis:
        movi = []
        link_text = li.find('a')
        href = link_text.get('href')
        href = url[:28] + '/' + href[8:]
        image = link_text.find("div", {'class': 'result-item-preview fadeIn animated'})
        img_str = image.get('style')
        img = img_str[22:len(img_str) - 27:1]
        name_title = link_text.find("div", {'class': 'results-item-title'}).text
        if (name_title == "" or name_title == " "):
            name_title = "нет названия"
        try:
            rating = link_text.find("span", {'class': 'results-item-rating'})
            rating = rating.find('span').text
        except:
            rating = " "
        year = link_text.find("span", {'class': 'results-item-year'}).text
        movi.append(name_title)
        movi.append(img)
        movi.append(rating)
        movi.append(year)
        movi.append(href)
        movi_list.append(movi)
        # print(name_title)
        # print(img)
        # print(rating)
        # print(year)
        # print(href)
        # print(link_text)
    return movi_list


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == 263993916:
        bot.reply_to(message, 'Здравствуй хозяин')
    else:
        bot.reply_to(message, 'Привет')


@bot.message_handler(commands=['help'])
def send_help(message):
    # bot.reply_to(message, 'Помощь')
    key = types.InlineKeyboardMarkup()
    button_weather = types.InlineKeyboardButton(text="Погода", callback_data="Weather")
    button_youtube = types.InlineKeyboardButton(text="Ютуб", callback_data="youtube")
    key.add(button_weather, button_youtube)
    bot.send_message(message.chat.id, "Помощь", reply_markup=key)


@bot.callback_query_handler(func=lambda but: True)
def send_help(but):
    if but.data == "Weather":
        print_weather(but)
        bot.send_message(but.message.chat.id, 'https://yandex.ru/pogoda/moscow')
    elif but.data == "youtube":
        bot.send_message(but.message.chat.id, 'https://www.youtube.com/')
    elif but.data == "choose_movi_yes":
        key = types.InlineKeyboardMarkup()
        button_comedy = types.InlineKeyboardButton(text="Камедия", callback_data="komediia")
        button_drama = types.InlineKeyboardButton(text="драма", callback_data="drama")
        key.add(button_comedy, button_drama)
        bot.send_message(but.message.chat.id, "выберите жанр", reply_markup=key)
    elif but.data == "choose_movi_not":
        print_movi(but)
    elif but.data == "komediia":
        print_movi(but)
    elif but.data == "drama":
        print_movi(but)


def print_movi(but):
    count = 1
    lst = []
    rand_page = random.randint(0, count_pages-1)
    rand_movi = random.randint(0, 59)
    while count <= count_pages:
        if but.data == "choose_movi_not":
            url = 'https://w25.zona.plus/movies?page=' + str(count)
        else:
            url = 'https://w25.zona.plus/movies/filter/genre-' + but.data + '/auto/ru?page=' + str(count)
        lst.append(pars_movi_page(url))
        count += 1
    bot.send_message(but.message.chat.id, lst[rand_page][rand_movi][0])
    bot.send_message(but.message.chat.id, lst[rand_page][rand_movi][1])
    bot.send_message(but.message.chat.id, lst[rand_page][rand_movi][4])
    print(lst[rand_page][rand_movi][0])


def print_weather(but):
    url = 'https://yandex.ru/pogoda/moscow/'
    lst = pars_weather_page(url)
    bot.send_message(but.message.chat.id, "Сейчас: " + lst[0][0])
    # bot.send_message(but.message.chat.id, "На улице: " + lst[0][1])
    bot.send_message(but.message.chat.id, "На улице: " + lst[0][1])
    bot.send_message(but.message.chat.id, "Ощущается как " + lst[0][2])
    print(lst[0][0])


@bot.message_handler(commands=['url'])
def url(message):
    markup = types.InlineKeyboardMarkup()
    btn_my_site = types.InlineKeyboardButton(text='Наш сайт', url='https://habrahabr.ru')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "Нажми на кнопку и перейди на наш сайт.", reply_markup=markup)


@bot.message_handler(commands=['share'])
def switch(message):
    markup = types.InlineKeyboardMarkup()
    switch_button = types.InlineKeyboardButton(text='Share', switch_inline_query="Telegram")
    markup.add(switch_button)
    bot.send_message(message.chat.id, "Выбрать чат", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def upper(message: Message):
    message.text = message.text.lower()
    val = message.text.find("хочу посмотреть")
    if message.text == 'ютуб':
        # with urllib.request.urlopen('http://python.org/') as response:
        #     html = response.read()
        bot.reply_to(message, 'https://www.youtube.com/')
    elif message.text == 'погода':
        key = types.InlineKeyboardMarkup()
        button_choose_weather = types.InlineKeyboardButton(text="погода", callback_data="Weather")
        key.add(button_choose_weather)
        bot.send_message(message.chat.id, "нажми кнопку", reply_markup=key)
        # bot.reply_to(message, 'https://yandex.ru/pogoda/moscow')
    elif message.text == 'кино':
        url = 'https://w25.zona.plus/movies?page='
        key = types.InlineKeyboardMarkup()
        button_choose_movi_yes = types.InlineKeyboardButton(text="да", callback_data="choose_movi_yes")
        button_choose_movi_not = types.InlineKeyboardButton(text="нет", callback_data="choose_movi_not")
        key.add(button_choose_movi_yes, button_choose_movi_not)
        bot.send_message(message.chat.id, "хотите выбрать жанр?", reply_markup=key)
    elif message.text == 'хочу посмотреть':
        bot.reply_to(message, 'https://yandex.ru/pogoda/moscow')
    else:
        bot.reply_to(message, "Я тупой и не понимаю команду")


bot.polling()
