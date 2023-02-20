# Car Picker Telegram Bot

Telegram bot that helps users choose a car. It asks a short quiz and suggests matching cars from a PostgreSQL catalog.

## Features

- `/start`, `/quiz`, `/results`, `/help` commands
- Quiz with inline answers
- Car recommendations with photos
- Results history stored in PostgreSQL

## Tech stack

Python, pyTelegramBotAPI, PostgreSQL, psycopg2

## Getting started

```bash
pip install pyTelegramBotAPI psycopg2
export TELEGRAM_BOT_TOKEN=...
export DB_PASSWORD=...
python bot.py
```
