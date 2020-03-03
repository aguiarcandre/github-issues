# Importa bibliotecas

from github import Github
from datetime import datetime
from google.cloud import firestore
import config


def get_gh_issues():
  try:
    # Search query to GitHub
    search_query = f'label:"good first issue" language:python is:open no:assignee created:>={last_issue["created_at"]}'

    # Faz chamada para API do GitHub
    issues = g.search_issues(search_query, sort="created")

    return issues
  except Exception as e:
    print(e)
    return None

def process_issues(issues):
  # Variables
  issues_list = []
  first_issue = True

  for issue in issues:
    # Min number of stars
    min_stars = 100
    # Check if the actual issue is not the last_issue
    if last_issue["id"] != issue.id and issue.repository.stargazers_count >= min_stars:
      issues_list.append({
          'Title': issue.title,
          'Created at': issue.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
          'Link': issue.html_url,
          'Repo stars': issue.repository.stargazers_count
      })
      # Print to development log
      for key, item in issues_list[-1].items():
          print(f'{key}: {item}')
      print('###############################################')
      # If first issue of the iteration, update last_issue values
      if first_issue:
        last_issue["id"] = issue.id
        last_issue["created_at"] = issue.created_at.strftime('%Y-%m-%dT%H:%M:%S')
        first_issue = False
  if len(issues_list) == 0:
    return None
  else:
    return issues_list


if __name__ == '__main__':
  # Autentica com Github e Firestore
  g = Github(config.github)
  db = firestore.Client().from_service_account_json('secrets/gh-issues-269718-3bc3674c82c3.json')

  # Initialize firestore database and get last_issue
  last_issue = db.collection('last-issue').document('0').get().to_dict()

  issues = get_gh_issues()
  if issues is not None:
    result = process_issues(issues)

  if result is not None:
    db.collection('last-issue').document('0').set(last_issue)
  else:
    print('Sem novidades')