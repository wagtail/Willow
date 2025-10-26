"""
Called by GitHub Action when the nightly build fails.

This reports an error to the #nightly-build-failures Slack channel.
"""

import os

import requests

if "SLACK_WEBHOOK_URL" in os.environ:
    # GitHub Actions environment variables
    WORKFLOW_NAME = os.environ.get("GITHUB_WORKFLOW", "workflow")
    REPO = os.environ.get("GITHUB_REPOSITORY", "")
    RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
    RUN_URL = f"https://github.com/{REPO}/actions/runs/{RUN_ID}"

    print("Reporting to #nightly-build-failures slack channel")  # noqa: T201

    message = {
        "text": ":warning: Willow nightly test failed",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Willow's nightly tests against a nightly version of Pillow failed.\nCan someone please check what is going on?\nWorkflow that failed: <{RUN_URL}|{WORKFLOW_NAME}>",
                },
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "This message was automatically posted by GitHub Actions.",
                    }
                ],
            },
        ],
    }
    resp = requests.post(os.environ["SLACK_WEBHOOK_URL"], json=message)
    resp.raise_for_status()
    print("Slack message sent successfully")  # noqa: T201

else:
    print(  # noqa: T201
        "Unable to report to #nightly-build-failures slack channel because SLACK_WEBHOOK_URL is not set"
    )
