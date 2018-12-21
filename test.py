# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "YOUR_TOKEN"
slack_client_id = "YOUR_CLIENT_ID"
slack_client_secret = "YOUR_CLIENT_SECRET"
slack_verification = "YOUR_VERIFICATION_TOKEN"

sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_free_game_keywords_(text):


    url = "https://play.google.com/store/apps/category/GAME/collection/topselling_free"

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # 함수를 구현해 주세요
    keywords = []
    for data in (soup.find_all("div", class_="card-content")):
        print(data)
        result = ''
        for d in data.find_all("a", class_="title"):
            result += d.get_text()
            result += '은(는) '
        for e in data.find_all("div", class_="tiny-star"):
            f = e.find("div")["style"]
            f = f.split()[1][:2]
            result += f + "점입니다."
        keywords.append(result)
    return u'\n'.join(keywords[:20])

# 크롤링 함수 구현하기
def _crawl_paid_game_keywords(text):


    url = "https://play.google.com/store/apps/category/GAME/collection/topselling_paid"

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # 함수를 구현해 주세요
    keywords = []

    for data in (soup.find_all("div", class_="card-content")):
        result = ''
        for d in data.find_all("a", class_="title"):
            result += d.get_text()
            result += '은(는) '
        for e in data.find_all("div", class_="tiny-star"):
            z = e.find("div")["style"]
            z = z.split()[1][:2]
            result += z + "점이고, 가격은 "
        for f in data.find_all("span", class_="display-price"):
            y = f.get_text().replace("\\", '')
            result += y + "입니다."
            break

        keywords.append(result)
    return u'\n'.join(keywords[:20])

# 크롤링 함수 구현하기
def _crawl_topgrossing_game_keywords(text):


    url = "https://play.google.com/store/apps/category/GAME/collection/topgrossing"

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # 함수를 구현해 주세요
    keywords = []

    for data in (soup.find_all("div", class_="card-content")):
        result = ''
        for d in data.find_all("a", class_="title"):
            result += d.get_text()
            result += '은(는) '
        for e in data.find_all("div", class_="tiny-star"):
            z = e.find("div")["style"]
            z = z.split()[1][:2]
            result += z + "점입니다. "

        keywords.append(result)
    return u'\n'.join(keywords[:20])

# 크롤링 함수 구현하기
def _crawl_famous_game_keywords(text):


    url = "https://play.google.com/store/apps/collection/cluster?clp=ogoKCAQqAggBUgIIAQ%3D%3D:S:ANO1ljLEbPM&gsr=Cg2iCgoIBCoCCAFSAggB:S:ANO1ljIL2pc"

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # 함수를 구현해 주세요
    keywords = []
    i = 0
    for data in (soup.find_all("div", class_="card-content")):
        i += 1
        result = ''
        for d in data.find_all("a", class_="title"):
            result += str(i) + ". "
            result += d.get_text()
            result += '은(는) '
        for e in data.find_all("div", class_="tiny-star"):
            z = e.find("div")["style"]
            z = z.split()[1][:2]
            result += z + "점입니다. "

        keywords.append(result)
    return u'\n'.join(keywords[:20])

def _crawl_paid_game_link_keywords(text):
    url = "https://play.google.com/store/apps/category/GAME/collection/topselling_paid"

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # 함수를 구현해 주세요
    keywords = ["here"]
    res = []
    for data in (soup.find_all("div", class_="card-content")):
        result = ''
        r = {}
        link = "https://play.google.com/" + data.find("a")["href"]
        print(link)
        for d in data.find_all("a", class_="title"):
            t = d.get_text()
        for e in data.find_all("div", class_="tiny-star"):
            z = e.find("div")["style"]
            z = z.split()[1][:2]
            result += z + "점이고, 가격은 "
        for f in data.find_all("span", class_="display-price"):
            y = f.get_text().replace("\\", '')
            result += y + "입니다."
            break

        r["title"] = t
        r["title_link"] = link
        r["text"] = result

        res.append(r)

        if len(res) > 19:
            break
    keywords.append(res)
    return keywords

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        if "도움" in text:
            keywords = '인기 게임 / 유료 게임 / 게임 매출 순위 / 인기 앱'
        if "인기 게임" in text:
            keywords = _crawl_free_game_keywords_(text)
        if "유료" in text:
            keywords = _crawl_paid_game_keywords(text)
        if "매출" in text:
            keywords = _crawl_topgrossing_game_keywords(text)
        if "인기 앱" in text:
            keywords = _crawl_famous_game_keywords(text)
        if "링크" in text:
            keywords = _crawl_paid_game_link_keywords(text)

        if type(keywords) is list:
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords[0],  # pretext
                attachments=keywords[1]  # dictionary list
            )
        # 그 외의 경우에는 일반적으로 처리
        else:
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords
            )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)
    print("called")
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":"application/json"})

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droidsyou're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)