import datetime
import os
import sys
import json
import requests

YEAR = os.environ.get('YEAR')
LEADERBOARD_ID = os.environ.get('LEADERBOARD_ID')
SESSION_ID = os.environ.get('SESSION_ID')
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK')

def get_leaderboard_url(year, id):
    return f"https://adventofcode.com/{year}/leaderboard/private/view/{id}"

def formatLeaderMessage(year, leaderboard_id, members):
    """
    Format the message to conform to Slack's API
    """
    message = ""

    # add each member to message
    for username, time, stars in members:
        message += f"*{username}* {stars} :star:\n"

    message += f"\n<{get_leaderboard_url(year, leaderboard_id)}|View Online Leaderboard>"

    return message

def parseMembers(members_json):
    """
    Handle member lists from AoC leaderboard
    """
    # get member name, score and stars
    members = [(m["name"], int(m["last_star_ts"]), m["stars"]) for m in members_json.values()]

    # sort members by stars, decending, then last_star, ascending 
    members.sort(key=lambda s: (-s[2], s[1]))

    return members

def postMessage(message):
    """
    Post the message to to Slack's API in the proper channel
    """
    payload = json.dumps({
        "icon_emoji": ":christmas_tree:",
        "username": "Advent Of Code Leaderboard",
        "text": message
    })

    requests.post(
        SLACK_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"}
    )


def lambda_handler(event, context):
    # make sure all variables are filled
    if LEADERBOARD_ID is None or SESSION_ID is None or SLACK_WEBHOOK is None or YEAR is None:
        return {
            'statusCode': 500,
            'body': json.dumps('Please ensure the variables are set before running')
        }

    # retrieve leaderboard
    r = requests.get(
        f"{get_leaderboard_url(YEAR, LEADERBOARD_ID)}.json",
        cookies={"session": SESSION_ID}
    )
    if r.status_code != requests.codes.ok: #pylint: disable=no-member
        return {
            'statusCode': 500,
            'body': json.dumps('Error retrieving leaderboard')
        }

    # get members from json
    members = parseMembers(r.json()["members"])

    # generate message to send to slack
    message = formatLeaderMessage(YEAR, LEADERBOARD_ID, members)

    # send message to slack
    postMessage(message)

    return {
        'statusCode': 200,
        'body': json.dumps('Leaderboard sent to slack')
    }
