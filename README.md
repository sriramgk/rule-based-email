# Rule based email operations
Python script that integrates with Gmail API and performs some rule based operations on emails.

## Pre-requisites
1. Python 3.8 or higher
2. pip
3. Virtualenv
4. Docker
5. Google account


## Setup

### Database

In both the below methods, table will automatically be created when the application is run.


#### Option 1: Docker

This is optional. If you don't have postgres installed on your system, you can use the docker-compose file to setup the database.

This will install the postgres database and pgadmin for easy database management.

```
docker compose build
docker compose up -d
```

Username and password for the database are already set in the docker-compose file.

#### Option 2: Database setup

If you already have a postgres database running, you can create a database named and add the database details in the `.env` file. 

### Setup virtual environment

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setup Google Client credentials

1. Make a folder named `credentials` in the root directory.
2. Go to [Google Developer Console](https://console.developers.google.com/)
3. Create a new project.
4. Enable Gmail API.
5. Create OAuth 2.0 Client ID.
6. Download the credentials file and save it as `credentials.json` in the `credentials` folder.
7. Add the `credentials.json` file path in the `.env` file.

## Run the application

1. Fetch emails from Gmail and store them in the database.

```
python email_handler.py
```

This will open a browser window asking for permission to access your Gmail account. Click on `Allow` to give permission.

2. Edit the rule JSON file `rules/email_rules.json` and set the required rules.

3. Run the rule based operations on the emails.

```
python apply_rule.py
```

## Run tests

```
pytest --ignore=storage
```
