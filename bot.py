from config import *
from requests import get
from os.path import exists
from telebot import TeleBot
from json import dump, load
from re import compile, match
from json.decoder import JSONDecodeError
from telebot.types import ReplyKeyboardMarkup
from requests.exceptions import ConnectionError
from xml.etree.ElementTree import ElementTree, fromstring

bot = TeleBot(bot_token)
new_config = "config.json"
if exists(new_config):
    with open(new_config, "r") as f:
        config = load(f)
    wled_ip = config["wled_ip"]
    presets = config["presets"]
else:
    config = {
        "wled_ip": wled_ip,
        "presets": presets}
    with open(new_config, "w") as f:
        dump(config, f)
wled_url = f"http://{wled_ip}/win"

def chose_action(button):
    global presets
    global white_id
    return {
        '◀': f"&P1=1&P2={presets}&PL=~-",
        '⚪': f"&PL={white_id}",
        '▶': f"&P1=1&P2={presets}&PL=~",
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
        wled_url = f"http://{message.text}/win"
        config["wled_ip"] = message.text
        with open(new_config, "w") as f:
            dump(config, f)
        response = f"WLED ip set to {message.text}"
    else:
        response = "Wrong ip format!"
    bot.reply_to(message, response)

def set_brightness(message):
    try:
        value = abs(int(float(message.text)))
        if value >= 255:
            value = 255
        action =  '&A=' + str(value)
        get_wled_response(action)
        bot.reply_to(message, f"Brightness set to {value}")
    except:
        bot.reply_to(message, "Something wrong! Write a natural number between 0 and 255")

def set_presets(message):
    try:
        value = abs(int(float(message.text)))
        if value <= 255 and value >= 0:
            global presets 
            presets = value
            config["presets"] = message.text
            with open(new_config, "w") as f:
                dump(config, f)
            bot.reply_to(message, f"Max preset index set to {presets}")
    except:
        bot.reply_to(message, "Something wrong! Write a natural number between 0 and 255")

def get_wled_response(action):
    root = ElementTree(fromstring(get(wled_url + action, timeout=10,
        verify=False).content)).getroot()
    return get_info()

def format_message_response(response, task):
    brightness = response['brightness']
    info = 'Brightness ' + brightness
    if task ==  '◐' and brightness == '0':
        state = 'off❌'
    elif task ==  '◐' and brightness != '0':
        state = 'on✅'
    else:
        state = '🆗'
        info = get_info()['full']
    return f"{state}\n{info}"

def get_info():
    root = ElementTree(fromstring(get(wled_url,
        timeout=10, verify=False).content)).getroot()
    brightness = root[0].text
    presets = root[19].text
    return {'brightness': brightness,
                'presets': presets,
                  'full': f'Brightness {brightness}\nPreset {presets}'}
 
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
        response = get_info()['full']
        bot.reply_to(message, response)
    except ConnectionError as e:
        bot.reply_to(message, "ERROR\nIp address is not reachable")
        print(e)

@bot.message_handler(func=lambda message: message.chat.id in white_list)
def handle_message(message):
    task = message.text
    if task in ['◀', '⚪', '▶', '◐', '☀', '🔅', '🔆']:
        action = chose_action(task)
        try:
            response = format_message_response(get_wled_response(action), task)
            bot.reply_to(message, response)
        except ConnectionError as e:
            bot.reply_to(message, "ERROR\nIp address is not reachable")
            print(e)
        except IndexError as e:
            bot.reply_to(message, "ERROR\nWrong ip address (IndexError)")
            print(e)
        except Exception as e:
            bot.reply_to(message, "ERROR\nUnknown error occurred")
            print(e)
    elif task == '🌓':
        markup = ReplyKeyboardMarkup(one_time_keyboard=False)
        markup.add('🔅', '✍', '🔆', '←', '◐', '☀')
        bot.reply_to(message, '🌝Brightness change mode🌚', reply_markup=markup)
    elif task == '←':
        markup = ReplyKeyboardMarkup(one_time_keyboard=False)
        markup.add('◀', '⚪', '▶', '🌓', '◐')
        bot.reply_to(message, '⚙Main control panel⚙', reply_markup=markup)
    elif task == '✍':
        bot.reply_to(message, "Write a brightness (0..255)")
        bot.register_next_step_handler(message, set_brightness)
    else:
        pass

bot.polling(none_stop=True, timeout=300)
