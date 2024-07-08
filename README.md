# Just Free Games

## Overview

<a target="_blank" href="https://www.just-free-games.com/">www.just-free-games.com</a> is a platform for discovering and collecting giveaways and freebies for your favorite games.

Here you can find the backend code responsible for collecting the data shown on the website, while the frontend code is not available to the public since it is built on top of a paid template.

Currently, the project is hosted on a Raspberry Pi that automatically updates a portion of the database every 5 minutes on the website, to ensure near-instantaneous responses and avoid exposing the Pi over internet.

## Technical Details

This project utilizes the Django framework to manage the backend infrastructure, routing, and database interactions; it is divided into two key components: the scraper and the chatbot.

## Workflow

1. Data Collection (Scraper):

   - The scraper reads from multiple websites and APIs.
   - The collected data is parsed and stored locally in an SQLite database.

2. Data Review and Publishing (Chatbot):

   - The chatbot sends the stored data to an administrator via Telegram.
   - The administrator reviews the giveaways through Telegram.
   - The approved giveaways are posted to social media channels (Twitter and Telegram) and the website.

## Installation

1. Clone the repository:

```
git clone git@github.com:catruzz/just-free-games-backend.git
```

2. Save an `.env` file to the root folder containing the following variables:

```
# PRODUCTION
DEBUG='False'
ENV='production'

# DEV
DEBUG='True'
ENV='development'

# ALL
DJANGO_SECRET_KEY='XXX'
DJANGO_SETTINGS_MODULE='XXX'
DB_BACKUP_SCRIPT='XXX'
FTP_HOST='XXX'
FTP_USERNAME='XXX'
FTP_PASSWORD='XXX'
ITAD_API_KEY='XXX'
ITAD_USERNAME='XXX'
ITAD_PASSWORD='XXX'
REDDIT_CLIENT_ID='XXX'
REDDIT_CLIENT_SECRET='XXX'
REDDIT_PASSWORD='XXX'
REDDIT_USER_AGENT='XXX'
REDDIT_USERNAME='XXX'
STEAM_GRID_DB_API_KEY='XXX'
TELEGRAM_BOT_API_USERNAME='XXX'
TELEGRAM_BOT_API_PASSWORD='XXX'
TELEGRAM_BOT_TOKEN='XXX'
TELEGRAM_TEST_BOT_TOKEN='XXX'
TELEGRAM_DEVELOPER_CHAT_ID='XXX'
TELEGRAM_CHANNEL_CHAT_ID='XXX'
TELEGRAM_TEST_CHANNEL_CHAT_ID='XXX'
TWITTER_CONSUMER_KEY='XXX'
TWITTER_CONSUMER_SECRET='XXX'
TWITTER_ACCESS_TOKEN='XXX'
TWITTER_ACCESS_TOKEN_SECRET='XXX'
```

3. Install dependencies:

```
npm install
```

```
pip install -r <(pipenv requirements)
```

4. Apply migrations:

```
python3 manage.py migrate
```

5. Run the server:

```
python3 manage.py runserver
```

6. Run the scraper:

```
python3 launch_scraper.py
```

7. Run the chatbot:

```
python3 launch_chatbot.py
```

## Manage Processes

To schedule all the processes, you can use the <a target="_blank" href="https://pm2.io/">PM2 Process Manager</a>: please have a look at the configuration file <a target="_blank" href="ecosystem.config.js">ecosystem.config.js</a>, which contains the needed configuration to run the server, the scraper, the chatbot, but also pull the repo and upload the project dependencies at a specific time or when a file change occurs.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
If you would like to support the project financially, please consider to make a donation:

- <a target="_blank" href="https://www.patreon.com/catruzz">Patreon</a>
- <a target="_blank" href="https://www.paypal.com/paypalme/catruzz">Paypal</a>

## License

This project is licensed under the GNU GPLv3 License - see the <a href="LICENSE">LICENSE</a> file for details.
