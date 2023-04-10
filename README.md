# Poe chatbot for telegram

A lightweight poe chatbot for telegram  


### Usage

#### Finding Your Token:

Log into [Poe](https://poe.com/) on any web browser, then open your browser's developer tools (also known as "inspect") and look for the value of the `p-b` cookie in the following menus:

- Chromium: Devtools > Application > Cookies > poe.com
- Firefox: Devtools > Storage > Cookies
- Safari: Devtools > Storage > Cookies


#### Create config.json
> remove the comments before use
```js

{
  "token": ":", // telegram bot token
  "chatbot": {
      "0": { // your telegram user id
          "token": "", "", // poe token
          "bot": "chinchilla" // poe bot name
      }
  }
}
```

#### Run

1. docker
```shell
docker pull ghcr.io/tbxark/poe-telegram-bot:latest
docker run -d --name poe-telegram-bot -v /root/poe-telegram-bot/config.json:/app/config.json ghcr.io/tbxark/poe-telegram-bot:latest
```

2. manual
```shell
git clone https://github.com/TBXark/poe-telegram-bot.git
cd poe-telegram-bot
pip install -r requirements.txt
python main.py -c config.json
```
