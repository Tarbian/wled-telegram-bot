from config import *
from requests import get
from telebot import TeleBot
from json import dump, load
from re import compile, match
from telebot.types import ReplyKeyboardMarkup
from requests.exceptions import ConnectionError
from xml.etree.ElementTree import ElementTree, fromstring

bot = TeleBot(bot_token)

try:
    with open("wled_ip.json") as f:
        wled_url = "http://" + load(f) + "/win"
except FileNotFoundError:
    wled_url = "http://" + wled_ip + "/win"
    with open("wled_ip.json", "w") as f:
            dump(wled_ip, f)

try:
    with open("presets.json") as f:
        presets = load(f)
except FileNotFoundError:
    with open("presets.json", "w") as f:
            dump(presets, f)

def chose_action(button):
    global presets
    global white_id
    return {
        '◀': "&P1=1&P2=" + presets + "&PL=~-",
        '⚪': "&PL=" + white_id,
        '▶': "&P1=1&P2=" + presets + "&PL=~",
        '◐': "&T=2",
        '☀': "&A=255",
        '🔅': "&A=~-30",
        '🔆': "&A=~30"
    }[button]

def is_valid_ip(ip):
    pattern = compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    return True if pattern.match(ip) else False
    
def set_ip(message):
    wled_ip = message.text
    global wled_url
    if is_valid_ip(wled_ip) == True:
        wled_url = "http://" + message.text + "/win"
        with open("wled_ip.json", "w") as f:
            dump(wled_ip, f)
        response = "WLED ip set to " + message.text
    else:
        response = "Wrong ip format!"
    bot.reply_to(message, response)

def set_bright(message):
    try:
        value = abs(int(float(message.text)))
        if value >= 255:
            value = 255
        action =  '&A=' + str(value)
        get(wled_url + action, timeout=10, verify=False)
        bot.reply_to(message, "Brightness set to " + str(value))
    except:
        bot.reply_to(message, "Something wrong! Write a natural number between 0 and 255")

def set_presets(message):
    try:
        value = abs(int(float(message.text)))
        if value <= 255 and value >= 0:
            global presets 
            presets = message.text
            with open("presets.json", "w") as f:
                dump(presets, f)
            bot.reply_to(message, "Max preset index set to " + presets)
    except:
        bot.reply_to(message, "Something wrong! Write a natural number between 0 and 255")
 
@bot.message_handler(func=lambda message: message.chat.id in white_list, commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=False)
    markup.add('◀', '⚪', '▶', '🌓', '◐')
    bot.reply_to(message, '🆗 Bot is alive! 🆗\nWrite /help for info!', reply_markup=markup)

@bot.message_handler(func=lambda message: message.chat.id in white_list, commands=['help'])
def help(message):
    global help_message
    bot.reply_to(message, help_message)

@bot.message_handler(func=lambda message: message.chat.id in white_list, commands=['correct_ip'])
def correct_ip(message):
    bot.reply_to(message, "Write new ip of your WLED in format xxx.xxx.xxx.xxx")
    bot.register_next_step_handler(message, set_ip)

@bot.message_handler(func=lambda message: message.chat.id in white_list, commands=['correct_presets'])
def correct_presets(message):
    bot.reply_to(message, "Write a number of presets (0..255)")
    bot.register_next_step_handler(message, set_presets)

@bot.message_handler(func=lambda message: message.chat.id in white_list, commands=['status'])
def status(message):
    try:
        root = ElementTree(fromstring(get(wled_url,
            timeout=10, verify=False).content)).getroot()
        bright = root[0].text
        preset = str(int(root[19].text) + 1)
        response = 'Brightness ' + bright + '\nPreset ' + preset
        bot.reply_to(message, response)
    except ConnectionError as e:
        bot.reply_to(message, "ERROR\nIp address is not reachable")
        print(e)
    
@bot.message_handler(func=lambda message: message.chat.id in white_list)
def switch(message): 
    task = message.text
    if task in ['◀', '⚪', '▶', '◐', '☀', '🔅', '🔆']:
        action = chose_action(task)
        try:
            root = ElementTree(fromstring(get(wled_url + action,
                timeout=10, verify=False).content)).getroot()
            bright = root[0].text
            preset = str(int(root[19].text) + 1)
            if task == '◐' and bright == '0':
                response = 'off❌' + '\nBrightness ' + bright + '\nPreset ' + preset
            elif task == '◐' and bright != '0':
                response = 'on✅' + '\nBrightness ' + bright + '\nPreset ' + preset
            else:
                response = task + '\nBrightness ' + bright + '\nPreset ' + preset
            bot.reply_to(message, response)
        except ConnectionError as e:
            bot.reply_to(message, "ERROR\nIp address is not reachable")
            print(e)
        except IndexError as e:
            bot.reply_to(message, "ERROR\nWrong ip address (IndexError)")
            print(e)
        except:
            bot.reply_to(message, "ERROR\nIdk what is wrong")
    elif task == '🌓':
        markup = ReplyKeyboardMarkup(one_time_keyboard=False)
        markup.add('🔅', '✍', '🔆', '←', '◐', '☀')
        bot.reply_to(message, '🌝Brightness change mode🌚', reply_markup=markup)
    elif task == '←':
        markup = ReplyKeyboardMarkup(one_time_keyboard=False)
        markup.add('◀', '⚪', '▶', '🌓', '◐')
        bot.reply_to(message, '⚙Main control pannel⚙', reply_markup=markup)
    elif task == '✍':
        bot.reply_to(message, "Write a brightness (0..255)")
        bot.register_next_step_handler(message, set_bright)
    else:
        pass

bot.polling(none_stop=True, timeout=300)