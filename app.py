import os, tg, firedb

from github import Github
from datetime import datetime
from flask import Flask

# Initialize Flask app
app = Flask(__name__)

# Auth
g = Github(os.environ["GH_TOKEN"])


def get_gh_issues(g, last_issue, search):
    """Call GitHub API and fetch new issues based on user criterias"""
    try:
        # Search query to GitHub
        search_query = f'{search["query"]} {search["query_template"]} created:>={last_issue["created_at"]}'

        # Call Github API
        issues = g.search_issues(search_query, sort="created")

        return issues
    except Exception as e:
        error = f"Error during 'app.get_gh_issues()' execution: {e}"
        tg.send_error_message(error)


def process_issues(issues, last_issue, min_stars):
    """Filter new issues received from Github and return a list of dicts"""
    try:
        issues_list = []
        first_issue = True
        min_repo_stars = min_stars

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
                    new_last_issue = {
                        "id": issue.id,
                        "created_at": issue.created_at.strftime("%Y-%m-%dT%H:%M:%S")
                    }
                    firedb.update_document("last_issue", new_last_issue)
                    first_issue = False
        if len(issues_list) == 0:
            return None
        else:
            return issues_list
    except Exception as e:
        error = f"Error during 'app.process_issues()' execution: {e}"
        tg.send_error_message(error)


@app.route("/")
def main():
    try:
        # Get last issue and search data
        last_issue = firedb.get_document("last_issue")
        search = firedb.get_document("search")

        # Fetch new issues from Github API
        issues = get_gh_issues(g, last_issue, search)

        # Filter new issues
        filtered_issues = process_issues(issues, last_issue, search["min_stars"])

        # If filtered issues contains new data, send to telegram
        if filtered_issues is not None:
            msg_status = tg.send_issues(filtered_issues)
        return '', 200
    except Exception as e:
        error = f"Error during 'app.main()' execution: {e}"
        tg.send_error_message(error)
        return '', 500


port = int(os.environ.get("PORT", 8080))
if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=port)
