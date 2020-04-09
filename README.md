# zoneh
Zone-H cybercrime archive monitoring telegram bot.

![zoneh](https://github.com/tropicoo/zoneh/blob/master/img/scr.png)

# Disclaimer
Intended to use only for investigation/research purpose.

# Installation
Make sure you have Python >= 3.6

`clone` repo and install dependencies using `pip3`.

```
git clone https://github.com/tropicoo/zoneh.git
pip3 install -r requirements.txt
```

# Configuration
First of all you need to [create Telegram Bot](https://core.telegram.org/bots#6-botfather)
 and obtain its token.

Before starting bot needs to be configured.
Configuration is simply stored in **JSON** format.

Copy default configuration file `config-template.json`, which comes with default template,
to `config.json` and edit:
```json
{
  "telegram": {
    "token": "",
    "allowed_user_ids": []
  },
  "log_level": "DEBUG",
  "zoneh": {
    "archive": "special",
    "filters": {
      "countries": [],
      "domains": [],
      "notifiers": []
    },
    "rescan_period": 1800,
    "random_ua": true
  }
}
```

To get things done follow the next steps:
1. Put the obtained bot token to `token` key as string.
2. [Find](https://stackoverflow.com/a/32777943) your Telegram user id
and put it to `allowed_user_ids` list as integer value. Multiple ids can
be used, just separate them with a comma.
3. Choose Zone-H archive type to monitor: `archive`, `special` or `onhold`. 
Write to the `archive` key.
4. Write preferred filters to `filters` key:
    1. `countries`: [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
    country codes, e.g `['FR', 'BR']` for France and Brazil.
    2. `domains`: ending parts of domains e.g. `['.go.id']`
    3. `notifiers`: watch for submissions of specific notifiers.
   
5. Modify User-Agent headers written in `HEADERS` constant in `zoneh/const.py` if needed.

## Example configuration
```json
{
  "telegram": {
    "token": "3468953:ASOPFagAJCdPEZIVALKYhUFPVA",
    "allowed_user_ids": [
      111000111
    ]
  },
  "log_level": "DEBUG",
  "zoneh": {
    "archive": "special",
    "filters": {
      "countries": ["FR", "BR"],
      "domains": [".go.id"],
      "notifiers": ["BrB"]
    },
    "rescan_period": 1800,
    "random_ua": true
  }
}
```

# Usage
## Manual run
Simply run and see for welcome message in Telegram client.
> Note: This will log the output to the stdout/stderr (your terminal). Closing
the terminal will shutdown the bot.
```bash
python3 zbot.py

# Or make the script executable by adding 'x' flag
chmod +x zbot.py
./zbot.py
```
## Running by Docker Compose
Build image and run the container
```bash
sudo docker-compose build && sudo docker-compose up
```

# Misc
| Command | Description                                      |
|:--------|:-------------------------------------------------|
| /start  | Show help                                        |
| /help   | Show help                                        |
| /run    | Start data scraping                              |
| /csv    | Get csv data of gathered records during bot run  |
| /stop   | Fully terminate the bot                          |
