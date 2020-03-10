# Github issues
This project contains simple automation to fetch new Github issues based on user criteria and send it using a Telegram bot.

## Getting started
The code is divided into three files:
```python
# Main file
app.py
# Telegram functions
tg.py
# Database functions
firedb.py
```
The `app` file runs the [Flask](https://flask.pocoo.org/) web framework. When requested, it gets the data to build the query and send a call to Github API to fetch new issues. If any, it saves the new data and sends the issues by Telegram.

## Setup
This project runs on a [Docker](https://www.docker.com/) container and is hosted on [Google Cloud Platform](https://cloud.google.com/).

Main GCP services currently being used:

> Cloud Run - To host and run the container image

> Container Registry - To save the container image

> Cloud Firestore - Database

> Cloud Scheduler - To run the program on a defined schedule

To create a Telegram Bot, follow instructions [here](https://core.telegram.org/bots#3-how-do-i-create-a-bot).

It's important to export environment variables to correctly run the project.
```python
GH_TOKEN="Your Github personal access token"
TELEGRAM_TOKEN="Telegram bot token"
TELEGRAM_USERID="Your Telegram user id"
GOOGLE_APPLICATION_CREDENTIALS="Service account credentials with required permissions"
```
