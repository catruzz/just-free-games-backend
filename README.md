# JustFreeGames

Chatbot and Scaper to get games gievaways

## Raspberry setup

To get everything you need to run and debug the project, just follow the instructions below:

```
# GH CLI
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y

# login
gh auth login

# Zsh
apt install zsh
chsh -s $(which zsh)

# Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# firefox
sudo apt-get install firefox-geckodriver

# chromium
sudo apt-get install chromium-chromedriver

# SQLite Browser
apt-get install sqlitebrowser

# VSCode
apt install code

# NodeJS and NPM
apt-get install -y nodejs npm

# PM2
sudo npm install -g pm2
pm2 link l7heb2vcfi6f7vu dkl875823xdq8lh

# python3
apt-get install python3-pip

# pipenv
pip install pipenv --user

# dependencies
npm install
pip install -r <(pipenv requirements)

# githooks
git config --local core.hooksPath .github/hooks

# create superuser
python manage.py createsuperuser --username api_client_telegram --email catruzz@gmail.com

# dropdbox uploader
git clone https://github.com/andreafabrizi/Dropbox-Uploader.git
cd Dropbox-Uploader
sudo chmod +x dropbox_uploader.sh
./dropbox_uploader.sh
```

## Manage processes

If you want to schedule processes launch with PM2:

```
pm2 unstartup
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

and follow the prompt to properly set the system daemon.

When you need to kill and delete all the processes:

```
pm2 stop all && pm2 delete all
```

## Run locally

First of all, you need to export all the environment variables into a `.env` file.
You can find them in LastPass Notes. Just in case.

If you're in a test environment, remember to launch the project using a virtual environment:

```
pipenv shell
pipenv install
```

Then you can launch the applications locally (in different terminals):

```
python3 manage.py migrate && python3 manage.py runserver
python3 launch_scraper.py
python3 launch_chatbot.py
```

To launch tests, just go with the default `test` command:

```
python3 manage.py test
```

If you need to get access to the Django admin panel, be sure to have `DEBUG` variable set to `True`, or have localhost added to `ALLOWED_HOSTS` in `settings.py`. Then go to http://127.0.0.1:8000/admin/.
More info here: https://docs.djangoproject.com/en/4.1/intro/tutorial02/#introducing-the-django-admin.

## Troubleshooting

### Dependencies

If something goes wrong when installing the dependencies, try to delete both `Pipfile` and `Pipfile.lock`, then exit and remove the virtual env:

```
exit
pipenv --rm
```

and finally try to install all the dependencies from scratch, one at a time. E.g.:

```
pipenv install "beautifulsoup4==4.12.2" &&
pipenv install "django-cors-headers==4.2.0" &&
pipenv install "django-import-export==3.2.0" &&
pipenv install "django==4.2.5" &&
pipenv install "djangorestframework==3.14.0" &&
...
```

If you get the `externally-managed-environment` error, you can add the `--break-system-packages` argument when installing pacakges using `pip`.

### IDE

If your IDE is showing errors on some django imports, be sure to have selected the right python interpreter; you may have more than one on your machine, especially if you're using virtual environtments.
On VS Code, trigger the `Python: Select interpreter` flow and select the one you are using (e.g the one at your virtual environment location).
