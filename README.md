# Telegram Bot for [WLED](https://github.com/Aircoookie/WLED) Backlight Control
This Telegram bot allows you to control the backlight of your WLED lighting system using Telegram. You can change the brightness, presets, and other settings directly from the Telegram app.
## Getting Started
1.	Clone or download this repository.
   ```sh
   git clone https://github.com/Tarbian/wled-telegram-bot
   ```
2.	Set up your WLED device and put the IP address in `config.py` (can be changed latter)
   ```py
   wled_ip = "YOUR IP HERE" # 192.168.1.111
   ```
3.	Get the API token in [@BotFather](https://t.me/BotFather) and put in `config.py`
   ```py
   bot_token = "YOUR TOKEN HERE" # XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXX
   ```
4.	Add your ID and the ID of the people allowed to use the bot to `config.py` (can get be obtained from [THIS](https://t.me/getmyid_bot) bot)
   ```py
   white_list = [111111111, 222222222, ] # list of id`s who can control the bot
   ```
5.	Enter the id of the all-white preset and the total number of presets (can be changed latter) in `config.py`
   ```py
   white_id = "1"   # id of full white preset
   presets  = "10"  # number of presets
   ```
6.	Run the bot: 
```sh
python bot.py
```
## Usage
Once the bot is running, you can interact with it from Telegram using keybord. for detailed information send `/help` to the bot.
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
## Todo
- [ ] Improve code readability
- [ ] Add the ability to change the color
## License
This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
