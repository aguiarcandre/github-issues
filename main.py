# Importa bibliotecas

from github import Github
from datetime import datetime
from google.cloud import firestore

import config
import telegram


def get_gh_issues(g, last_issue):
  try:
    # Search query to GitHub
    search_query = f'label:"good first issue" -label:"question" language:python is:open no:assignee \
                      created:>={last_issue["created_at"]} -linked:pr'

    # Faz chamada para API do GitHub
    issues = g.search_issues(search_query, sort="created")

    return issues
  except Exception as e:
    print(e)
    return None

def process_issues(issues, last_issue):
  # Variables
  issues_list = []
  first_issue = True

  for issue in issues:
    # Min number of repo stars
    min_stars = 100
    # Check if the actual issue is not the last_issue
    if last_issue["id"] != issue.id and issue.repository.stargazers_count >= min_stars:
      issues_list.append({
          'Title': issue.title,
          'Link': issue.html_url,
          'Repo stars': issue.repository.stargazers_count
      })
      # If first issue (newer) of the iteration, update last_issue values
      if first_issue:
        last_issue["id"] = issue.id
        last_issue["created_at"] = issue.created_at.strftime('%Y-%m-%dT%H:%M:%S')
        first_issue = False
  if len(issues_list) == 0:
    return None
  else:
    return issues_list
  
def send_telegram_msg(bot, iss_list):
  try:
    if len(iss_list) > 0:
      for iss in iss_list:
        new_msg = ''
        for key, item in iss.items():
          new_msg += f'{key}: {item}\n'
        bot.send_message(chat_id=config.telegram_user_id, text=new_msg)
    return True
  except Exception as e:
    print(e)
    return None

def main():
  # Autentica com Github, Firestore e Telegram
  g = Github(config.github)
  db = firestore.Client().from_service_account_json('secrets/gh-issues-269718-3bc3674c82c3.json')
  bot = telegram.Bot(config.telegram)

  # Initialize firestore database and get last_issue
  last_issue = db.collection('last-issue').document('0').get().to_dict()

  # Get new issues from github api
  issues = get_gh_issues(g, last_issue)

  # Process new data received from github (if no errors)
  if issues is not None:
    result = process_issues(issues, last_issue)
  else:
    return

  # If the new data contains new issues based on criteria, send to telegram 
  if result is not None:
    msg_status = send_telegram_msg(bot, result)
  else:
    print('Sem novidades')
    return
  
  # If the message was successfully sent to telegram, update last_issue on firestore
  if msg_status:
    db.collection('last-issue').document('0').set(last_issue)


if __name__ == '__main__':
  main()
