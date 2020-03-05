import os, config, telegram
from github import Github
from datetime import datetime
from google.cloud import firestore
from flask import Flask

# Initialize Flask app
app = Flask(__name__)

# Auth
g = Github(os.environ["GH_TOKEN"])
bot = telegram.Bot(os.environ["TELEGRAM_TOKEN"])
db = firestore.Client()


def get_last_issue_data(db):
    """Get the last_issue data saved on Firestore"""
    try:
        last_issue = db.collection("last-issue").document("0").get().to_dict()
        return last_issue
    except Exception as e:
        raise Exception(f"Error getting Firestore last_issue: {e}")


def get_gh_issues(g, last_issue):
    """Call GitHub API and fetch new issues based on user criterias"""
    try:
        # Search query to GitHub
        search_query = f'label:"help wanted" -label:"question" language:python is:open no:assignee \
                      created:>={last_issue["created_at"]} -linked:pr'

        # Call Github API
        issues = g.search_issues(search_query, sort="created")

        return issues
    except Exception as e:
        raise Exception(f"Error calling Github API: {e}")


def process_issues(issues, last_issue):
    """Filter new issues received from Github and return a list of dicts"""
    issues_list = []
    new_last_issue = {}
    first_issue = True
    min_repo_stars = 100

    for issue in issues:
        if (
            last_issue["id"] != issue.id
            and issue.repository.stargazers_count >= min_repo_stars
        ):
            issues_list.append(
                {
                    "Title": issue.title,
                    "Link": issue.html_url,
                    "Repo stars": issue.repository.stargazers_count,
                }
            )
            # If first issue (newer) of the iteration, update last_issue value
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
    """Send a message to user by Telegram bot"""
    try:
        # If list (issues), iterate over and send to user
        if type(msg) is list:
            for iss in msg:
                new_msg = ""
                for key, item in iss.items():
                    new_msg += f"{key}: {item}\n"
                bot.send_message(chat_id=os.environ["TELEGRAM_USERID"], text=new_msg)
        # If not list (error), send message to user
        else:
            bot.send_message(chat_id=config.telegram_user_id, text=msg)
    except Exception as e:
        raise Exception(f"Error sending Telegram message: {e}")


def save_new_last_issue(db, new_last_issue):
    """Save the new last issue (newer) data on Firestore"""
    try:
        db.collection("last-issue").document("0").set(new_last_issue)
    except Exception as e:
        raise Exception(f"Error saving new last_issue to Firestore: {e}")


@app.route("/", methods=["GET"])
def main():
    try:
        # Get last issue data
        last_issue = get_last_issue_data(db)

        # Fetch new issues from Github API
        issues = get_gh_issues(g, last_issue)

        # Filter new issues
        filtered_issues, new_last_issue = process_issues(issues, last_issue)

        # If filtered issues contains new data, send to telegram
        if filtered_issues is not None:
            msg_status = send_telegram_msg(bot, filtered_issues)
            # If the message was successfully sent to telegram, update last issue on firestore
            save_new_last_issue(db, new_last_issue)
        return "Ok", 200
    except Exception as e:
        send_telegram_msg(bot, str(e))
        return "Error"


port = int(os.environ.get("PORT", 8080))
if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=port)
