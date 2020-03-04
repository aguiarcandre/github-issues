# Importa bibliotecas

from github import Github
from datetime import datetime
from google.cloud import firestore

import config
import telegram


def get_last_issue_data(db):
    try:
        last_issue = db.collection("last-issue").document("0").get().to_dict()
        return last_issue
    except Exception as e:
        raise Exception(f"Error getting Firestore last_issue: {e}")


def get_gh_issues(g, last_issue):
    try:
        # Search query to GitHub
        search_query = f'label:"good first issue" -label:"question" language:python is:open no:assignee \
                      created:>={last_issue["created_at"]} -linked:pr'

        # Call Github API
        issues = g.search_issues(search_query, sort="created")

        return issues
    except Exception as e:
        raise Exception(f"Error calling Github API: {e}")


def process_issues(issues, last_issue):
    # Variables
    issues_list = []
    new_last_issue = {}
    first_issue = True

    for issue in issues:
        # Min number of repo stars
        min_stars = 100
        # Check if the actual issue is not the last_issue
        if (
            last_issue["id"] != issue.id
            and issue.repository.stargazers_count >= min_stars
        ):
            issues_list.append(
                {
                    "Title": issue.title,
                    "Link": issue.html_url,
                    "Repo stars": issue.repository.stargazers_count,
                }
            )
            # If first issue (newer) of the iteration, update last_issue values
            if first_issue:
                new_last_issue["id"] = issue.id
                new_last_issue["created_at"] = issue.created_at.strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                first_issue = False
    if len(issues_list) == 0:
        return None, None
    else:
        return issues_list, new_last_issue


def send_telegram_msg(bot, msg):
    try:
        if type(msg) is list:
            for iss in msg:
                new_msg = ""
                for key, item in iss.items():
                    new_msg += f"{key}: {item}\n"
                bot.send_message(chat_id=config.telegram_user_id, text=new_msg)
        else:
            bot.send_message(chat_id=config.telegram_user_id, text=msg)
    except Exception as e:
        raise Exception(f"Error sending Telegram message: {e}")


def save_new_last_issue(db, new_last_issue):
    try:
        db.collection("last-issue").document("0").set(new_last_issue)
    except Exception as e:
        raise Exception(f"Error saving new last_issue to Firestore: {e}")


def main():
    try:
        # Autentica com Github, Firestore e Telegram
        g = Github(config.github)
        db = firestore.Client().from_service_account_json(
            "secrets/gh-issues-269718-3bc3674c82c3.json"
        )
        bot = telegram.Bot(config.telegram)

        # Initialize firestore database and get last_issue
        last_issue = get_last_issue_data(db)

        # Get new issues from github api
        issues = get_gh_issues(g, last_issue)

        # Process new data received from github (if no errors)
        result, new_last_issue = process_issues(issues, last_issue)

        # If the new data contains new issues based on criteria, send to telegram
        if result is not None:
            msg_status = send_telegram_msg(bot, result)
            # If the message was successfully sent to telegram, update last_issue on firestore
            save_new_last_issue(db, new_last_issue)
    except Exception as e:
        send_telegram_msg(bot, str(e))


if __name__ == "__main__":
    main()
