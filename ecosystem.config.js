// load .env variables
const path = require("path");
require("dotenv").config({ path: path.join(__dirname, ".env") });
const ignoreWatch = [
  "\\.git",
  "backend/scraper/__pycache__",
  "backend/scraper/suppliers/__pycache__",
  "fixtures",
  "logs",
  "node_modules",
  "db.sqlite3",
  "db.sqlite3-journal",
];

module.exports = {
  apps: [
    {
      name: "upload DB on Dropbox",
      script:
        "/home/catruzz/Dropbox-Uploader/dropbox_uploader.sh upload /home/catruzz/JustFreeGames/db.sqlite3 db.sqlite3",
      cron_restart: "*/5 * * * *",
      autorestart: false,
    },
    {
      name: "git pull",
      script: "git pull --rebase",
      cron_restart: "*/5 * * * *",
      autorestart: false,
    },
    {
      name: "pip install",
      script: "pip install -r <(pipenv requirements) --break-system-packages",
      autorestart: false,
      watch: ["Pipfile", "Pipfile.lock"],
      ignore_watch: ignoreWatch,
    },
    {
      name: "django_server",
      script:
        "sleep 5 && python3 manage.py migrate && python3 manage.py runserver",
      watch: true,
      ignore_watch: ignoreWatch,
    },
    {
      name: "export DB and upload to FTP",
      script:
        "sleep 15 && \
        python -Xutf8 manage.py dumpdata backend.giveaway --indent 2 -o fixtures/giveaways.json && \
        python -Xutf8 manage.py dumpdata backend.platform --indent 2 -o fixtures/platforms.json && \
        curl -T fixtures/giveaways.json ftp://${FTP_HOST}/fixtures/ --user ${FTP_USERNAME}:${FTP_PASSWORD} && \
        curl -T fixtures/platforms.json ftp://${FTP_HOST}/fixtures/ --user ${FTP_USERNAME}:${FTP_PASSWORD}",
      cron_restart: "*/5 * * * *",
      autorestart: false,
    },
    {
      name: "scraper",
      script: "sleep 15 && python3 launch_scraper.py",
      watch: false,
      cron_restart: "*/5 * * * *",
      autorestart: false,
      kill_timeout: 300000,
    },
    {
      name: "chatbot",
      script: "sleep 15 && python3 launch_chatbot.py",
      exp_backoff_restart_delay: 5000,
      watch: true,
      ignore_watch: ignoreWatch,
    },
  ],
};
