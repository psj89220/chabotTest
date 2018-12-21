# -*- coding: utf-8 -*-
import json
import os
import re
import time
import datetime
import urllib.request
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

ratings_data = pd.read_csv("C:\\Users\\student\\PycharmProjects\\myChatbot\\ml-latest-small\\ratings.csv")
movie_names = pd.read_csv("C:\\Users\\student\\PycharmProjects\\myChatbot\\ml-latest-small\\movies.csv")

slack_token = "YOUR_TOKEN"
slack_client_id = "YOUR_CLIENT_ID"
slack_client_secret = "YOUR_CLIENT_SECRET"
slack_verification = "YOUR_VERIFICATION_TOKEN"

sc = SlackClient(slack_token)


def _get_text(text):
    mon = re.compile('\d{1,2}월')
    rday = re.compile('\d{1,2}일')
    ddi = re.compile('[ㄱ-ㅎ가-힣]{1,3}띠')
    star = re.compile('[ㄱ-ㅎ가-힣]{1,3}자리')

    # 운세를 보고 싶은 날짜 구하기
    year = str(datetime.date.today().year)
    if '오늘' in text:
        month = str(datetime.date.today().month)
        day = str(datetime.date.today().day)
    else:
        month = mon.findall(text)[0].replace("월", "")
        if len(month) == 1:
            month = "0"+month
        day = rday.findall(text)[0].replace("일", "")
        if len(day) == 1:
            day = "0"+day

    # 날짜 예외 처리
    if int(day) < 0 or int(day) > 31:
        return '*정확한 날짜를 입력하세요*'

    if int(month) < 0 or int(month) > 12:
        return '*정확한 날짜를 입력하세요*'

    search_date = year + month + day

    # 특정 별자리, 띠
    user_ddi = ddi.findall(text)
    user_star = star.findall(text) if '별' not in text else []

    # 운세정보를 얻을 때 넘겨줄 사용자 정보
    info = ''

    # 사용자가 입력한 정보에 따른 분기
    if '오늘' in text:
        if '별자리' in text or len(user_star) > 0:
            if len(user_star) > 0:
                info = user_star[0]
            else:
                info = str('별자리')
            url = "https://www.ytn.co.kr/_ln/0121_" + search_date + "000000000" + str(2)
            return _crawl_star_luck(info, url, month, day)
        elif '띠별' in text or len(user_ddi) > 0:
            if len(user_ddi) > 0:
                info = user_ddi[0]
            else:
                info = str('띠별')
            url = "https://www.ytn.co.kr/_ln/0121_" + search_date + "000000000" + str(1)
            return _crawl_ddi_luck(info, url, month, day)
        else:
            title = '*검색어에 다음 단어들 중 한개를 포함시켜 주세요*'
            txt = '\n@ 별자리 \n @ 띠별 \n @ ~자리 \n @ ~띠\n'
            return title + txt
    else:
        if '별자리' in text or len(user_star) > 0:
            if len(user_star) > 0:
                info = user_star[0]
            else:
                info = str('별자리')
            url = "https://www.ytn.co.kr/_ln/0121_" + search_date + "000000000" + str(2)
            return _crawl_star_luck(info, url, month, day)
        elif '띠별' in text or len(user_ddi) > 0:
            if len(user_ddi) > 0:
                info = user_ddi[0]
            else:
                info = str('띠별')
            url = "https://www.ytn.co.kr/_ln/0121_" + search_date + "000000000" + str(1)
            return _crawl_ddi_luck(info, url, month, day)
        else:
            title = '*검색어에 다음 단어들 중 한개를 포함시켜 주세요*'
            txt = '\n@ 별자리 \n @ 띠별 \n @ ~자리 \n @ ~띠\n'
            return title + txt


# 별자리 운세정보 크롤링
def _crawl_star_luck(info, url, month, day):
    star_content = dict()
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
    content = soup.find("div", class_="article_paragraph").find("span").get_text()

    key = ''
    temp_list = []
    for line in content.split('\n'):
        if '제공=드림웍' in line:
            continue
        # key값 생성
        if line.startswith('['):
            key = ''
            temp_list = []
            # 별자리를 key 값으로 설정
            for char in line:
                if char == '[':
                    pass
                elif char == '리':
                    key += char
                    break
                else:
                    key += char
        # <br> 필터링
        elif not (line):
            pass
        else:
            temp_list.append(line)
        star_content[key] = temp_list

    # 특정 별자리가 아닌 별자리 전체를 검색
    if info == '별자리':
        res = []
        for key, value in star_content.items():
            title = "*" + key + " " + month + "월 " + day + "일" + " 운세 :*"
            txt = '\n\n'
            for text in star_content[key]:
                txt += text.replace(".", "\n") + "\n"
            res.append(title + txt)
        return u'\n'.join(res)

    # 특정 별자리만 검색
    else:
        res = {}
        for key, value in star_content.items():
            # 사용자가 입력한 별자리가 있으면 결과값으로 저장
            if key == info:
                title = "*" + key + " " + month + "월 " + day + "일" + " 운세 :*"
                txt = '\n\n'
                for text in star_content[key]:
                    txt += text.replace(".", "\n") + "\n"
                res = {title + txt}
                break
            # 별자리에 없는 별자리를 입력 ex) 잠자리
            else:
                title = "*정확한 별자리 정보를 입력해 주세요*"
                txt = "\n물병\t물고기\t양\t황소\n쌍둥이\t게\t사자\t처녀\n천칭\t전갈\t사수\t염소"
                res = {title + txt}
        return u'\n'.join(res)


# 띠별 운세정보 크롤링
def _crawl_ddi_luck(info, url, month, day):
    ddi_content = dict()
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
    content = soup.find("div", class_="article_paragraph").find("span").get_text()

    key = ''
    temp_list = []
    for line in content.split('\n'):
        if '제공=드림웍' in line:
            continue
        # key값 생성
        if line.startswith('['):
            key = ''
            temp_list = []
            # 띠를 key 값으로 설정
            for char in line:
                if char == '[':
                    pass
                elif char == ']':
                    break
                else:
                    key += char
        # <br> 필터링
        elif not (line):
            pass
        else:
            temp_list.append(line)
        ddi_content[key] = temp_list

    # 특정 띠가 아닌 띠 전체 검색
    if info == '띠별':
        res = []
        for key, value in ddi_content.items():
            title = "*" + key + " " + month + "월 " + day + "일" + " 운세 :*"
            txt = '\n\n'
            for text in ddi_content[key]:
                txt += text.replace(".", "\n") + "\n"
            res.append(title + txt)
        return u'\n'.join(res)

    else:
        res = {}
        for key, value in ddi_content.items():
            # 사용자가 입력한 띠가 있으면 결과값으로 저장
            if key == info:
                title = "*" + key + " " + month + "월 " + day + "일" + " 운세 :*"
                txt = '\n\n'
                for text in ddi_content[key]:
                    txt += text.replace(".", "\n") + "\n"
                res = {title + txt}
                break
            # 정확하지 않은 띠를 입력 ex) 허리띠
            else:
                title = "*정확한 띠 정보를 입력해 주세요*"
                txt = "\n쥐\t소\t호랑이\t토끼\n용\t뱀\t말\t양\n개\t돼지\t원숭이\t닭"
                res = {title + txt}
        return u'\n'.join(res)



def _crawl_music_keywords(text):
    # 여기에 함수를 구현해봅시다.
    url = "https://music.bugs.co.kr/chart"
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")
    keywords = []
    for i, tr in enumerate(soup.select("tbody tr")):
        if i < 10:
            music = {}
            music['ranking'] = tr.select("div strong")[0].get_text()
            music['title'] = tr.select("p.title a")[0].get_text()
            music['artist'] = tr.select(".artist a")[0].get_text()
            music['album'] = tr.select(".album")[0].get_text()
            keywords.append(music)

    stringTemplate = "%s위: %s / %s"
    titleString = 'Bugs 실시간 음악 차트 Top 10'
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return titleString + u'\n' + u'\n'.join(
        [stringTemplate % (music['ranking'], music['title'], music['artist']) for music in keywords])

def _movie_recommendation(text):
    ## ratings_data (ratings.csv)
    ## 사용자(userId)의 영화(movieId)에 대한 평가(rating) 데이터. userid, movieId, rating(1~5), timestamp 로 구성
    ## flask 내부의 method로 변경하면서 초기 생성부분으로 이동

    ## movie_names (movies.csv)

    ## 영화데이터. movieId, title, genres로 구성
    ## 추천 시스템을 content-based Filtering으로 구성하기 위해서는 아래 dataset의 genres를 이용해야 한다.
    ## flask 내부의 method로 변경하면서 초기 생성부분으로 이동

    movie_names_df = pd.DataFrame(movie_names)
    # print(movie_names.columns.tolist())

    ## movie_names와 ratings_data를 movieId를 기준으로 병합하여 하나의 테이블로 구성
    ## movie_data의 column구성은 userId, movieId, rating, timestamp, title, genres가 될 것이다.
    ## 특정 user가 추천한 영화의 이름이 무엇인지 볼 수 있게 되었다.
    movie_data = pd.merge(ratings_data, movie_names, on='movieId')
    user_movie_rating = movie_data.pivot_table(index='userId', columns='title', values='rating')
    # print(movie_data.columns.tolist())

    ## 같은 영화(=같은 movieId 혹은 같은 title(title은 동명의 영화가 있을수도 있지 않나?))의 유저 평가 점수들을 모두 묶어
    ## 평균 평가점수를 얻을 수 있다.
    # print(movie_data.groupby('title')['rating'].mean().head())

    ## 위에서 얻은 평균 평가점수를 sort하기 위해선 sort_values(by='DataFrame의 경우 기준 컬럼', ascending=오름차순여부(True|False)) 로 정렬가능
    # print(movie_data.groupby('title')['rating'].mean().sort_values(ascending=False).head())

    ## 전체 평가자 수가 1명 뿐이고, 해당 평가자가 5점을 준 경우 상위에 노출되는 상황 발생
    ## 위의 유저 평가의 평균값만으로 추천하기엔 정확도가 낮다!
    ## 평가자 수도 추가하여 추천 척도로 추가
    ratings_mean_count = pd.DataFrame(movie_data.groupby('title')['rating'].mean())
    ratings_mean_count['rating_counts'] = pd.DataFrame(movie_data.groupby('title')['rating'].count())
    # print(ratings_mean_count.head())

    ## 시각화 테스트
    # sns.set_style('dark')
    # %matplotlib inline
    #
    # plt.figure(figsize=(8,6))
    # plt.rcParams['patch.force_edgecolor'] = True
    # ratings_mean_count['rating_counts'].hist(bins=50)
    #
    # plt.figure(figsize=(8,6))
    # plt.rcParams['patch.force_edgecolor'] = True
    # ratings_mean_count['rating'].hist(bins=50)
    #
    # plt.figure(figsize=(8,6))
    # plt.rcParams['patch.force_edgecolor'] = True
    # sns.jointplot(x='rating', y='rating_counts', data=ratings_mean_count, alpha=0.4)
    ##
    print(text)
    titleEx = re.compile("[a-zA-Z 1-9]+")
    title_particle = titleEx.findall(text)[1]
    print(title_particle)

    for testTitle in movie_names_df['title'].values.tolist():
        k  = re.compile(" \(\d+\)$")
        result = k.findall(testTitle)
        if len(result) > 0:
            if title_particle == testTitle.replace(result[0], ''):
                title_particle = testTitle
        else:
            if title_particle == testTitle.strip():
                title_particle = testTitle
    print(title_particle)

    # title_particle = 'Forrest Gump (1994)'
    keywords = []
    ## 정확한 영화의 제목을 알고 있을 경우
    if title_particle in movie_names_df['title'].values.tolist():
        e = {}
        # print('There is exact movie')
        ratings = user_movie_rating[title_particle]
        movies_like_this = user_movie_rating.corrwith(ratings)
        corr_rate = pd.DataFrame(movies_like_this, columns=['Correlation'])
        corr_rate.dropna(inplace=True)

        corr = corr_rate.join(ratings_mean_count['rating_counts'])

        # print("Movies like ", title_particle + ":")
        # print(list(corr.index))
        corrlist = []
        for row in corr[(corr['rating_counts'] > 50)].sort_values('Correlation', ascending=False).head(10).iterrows():
            index, data = row
            rowtolist = [index, data.tolist()]
            corrlist.append(rowtolist)
        e['title'] = title_particle
        e['corr'] = corrlist
        if len(corrlist) > 0:
            keywords.append(e)
    ## 정확한 영화의 제목을 모르고 일부분만 알고 있을 경우
    ## df[df['title'].str.contains("hello")]
    else:
        # print('There is no exact movie')
        possible_titles = movie_names_df[movie_names_df['title'].str.contains(title_particle)]['title'].values
        # print("possible:", possible_titles.tolist())
        for title in possible_titles.tolist():
            e = {}
            ratings = user_movie_rating[str(title)]
            movies_like_this = user_movie_rating.corrwith(ratings)
            corr_rate = pd.DataFrame(movies_like_this, columns=['Correlation'])
            corr_rate.dropna(inplace=True)

            corr = corr_rate.join(ratings_mean_count['rating_counts'])

            # print("Movies like ", title + ":")
            # print(list(corr.index))
            # print(corr[(corr['rating_counts'] > 50)].sort_values('Correlation', ascending=False).head())

            corrlist = []
            for row in corr[(corr['rating_counts'] > 50)].sort_values('Correlation', ascending=False).head(
                    10).iterrows():
                index, data = row
                rowtolist = [index, data.tolist()]
                corrlist.append(rowtolist)
            e['title'] = title
            e['corr'] = corrlist
            if len(corrlist)>0:
                keywords.append(e)

    if len(keywords) > 0:
        titleString1 = "요청하신 영화와 유사한 이름의 영화에 대하여 각각 유사도 평가를 수행하여 나온 결과입니다."
        titleString2 = "영화 %s와 유사한 영화: "
        stringTemplate = "영화제목: %s   유사도: %s   추천수: %s"
        return titleString1 + u'\n' + u'\n'.join([(titleString2% e['title']) + u'\n\t' + u'\n\t'.join([stringTemplate % (corr[0], corr[1][0], corr[1][1]) for corr in e['corr']]) for e in keywords])
    else:
        return "영화 정보를 찾을 수 없습니다. 영화 제목을 제대로 입력하신 것 맞나요?"

# 네이버 영화 정보 크롤링 함수 구현하기
def _crawl_naver_keywords(text, order):
    # 여기에 함수를 구현해봅시다.
    url = "https://movie.naver.com/movie/running/current.nhn?view=list&tab=normal&order=" + order
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # 좋아요순
    if order == "likeCount":
        answer = "좋아요순으로 정렬한 결과입니다.\n"
    # 평점순
    elif order == "point":
        answer = "평점순으로 정렬한 결과입니다.\n"
    # 개봉순
    elif order == "open":
        answer = "개봉일순으로 정렬한 결과입니다.\n"

    movies = []
    for i, div in enumerate(soup.select(".lst_dsc")):
        if i < 20:
            movie = {}
            movie['title'] = ",".join([i.get_text() for i in div.select(".tit a")])
            movie['userRating'] = str(div.select("dd .num")[0].get_text())
            if order == 'open':
                movie['proRating'] = (
                    str(div.select("dd .num")[1].get_text()) if len(div.select("dd .num")) == 2 else " ")
            elif order == 'reserve':
                movie['reserveRate'] = ",".join([i.get_text() for i in div.select(".b_star .num")])
            movie['genre'] = [i.get_text() for i in div.select(".info_txt1 dd")[0].select(".link_txt a")]
            movie['director'] = [i.get_text() for i in div.select(".info_txt1 dd")[1].select(".link_txt a")]
            movie['cast'] = ([i.get_text() for i in div.select(".info_txt1 dd")[2].select(".link_txt a")] if len(
                div.select(".info_txt1 dd")) > 2 else [])
            if order == 'likeCount':
                movie['likeCount'] = ",".join([i.get_text().strip() for i in div.select("div.likeit_area")])
            movies.append(movie)

    # 한글 지원을 위해 앞에 unicode u를 붙힙니다.
    if order == "likeCount":
        stringTemplate = "%s 의 좋아요 수는 %s 입니다."
        return answer + u'\n' + u'\n'.join([stringTemplate % (movie['title'], movie['likeCount']) for movie in movies])
    elif order == "point":
        stringTemplate = "%s 의 사용자 평점은 %s 입니다."
        # return answer + u'\n' + u'\n'.join([movie['title'] + "의 사용자 평점은 " + movie['userRating'] for movie in movies])
        # print("methods:", u'\n'.join([stringTemplate % (movie['title'], movie['userRating']) for movie in movies]))
        return answer + u'\n' + u'\n'.join([stringTemplate % (movie['title'], movie['userRating']) for movie in movies])
    else:
        return answer + u'\n' + u'\n'.join([movie['title'] for movie in movies])

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


# ssafy식단 크롤링 함수 구현하기
def _crawl_ssafy_keywords(text):
    # 여기에 함수를 구현해봅시다.
    keywords = []

    now = time.localtime()
    week = ('월', '화', '수', '목', '금', '토', '일');
    # print('오늘 요일: %s요일' % ( week[now.tm_wday] ))

    menus = [
          {"date": "181219", "type": "A", "menu": ["콩나물밥*양념장", "된장찌개", "떡갈비조림", "가지나물", "치커리유자청무침", "배추김치", "수정과/숭늉"], "calorie": 1114}
        , {"date": "181219", "type": "B", "menu": ["홍합짬뽕", "MINI쌀밥", "만두탕수", "스크램블에그", "단무지무침", "배추김치", "수정과/숭늉"], "calorie": 1041}
        , {"date": "181220", "type": "A", "menu": ["경상도식고깃국", "강낭콩밥*쌀밥", "깻잎해물전", "탕평채", "건파래볶음", "석박지", "미숫가루/숭늉"], "calorie": 765}
        , {"date": "181220", "type": "B", "menu": ["마파두부덮밥", "만가닥맑은국", "꼬마돈가스*케찹", "콩나물겨자채무침", "콘버터구이", "배추김치", "미숫가루/숭늉"], "calorie": 1202}
        , {"date": "181221", "type": "A", "menu": ["순대국밥", "잡곡밥*쌀밥", "김치전", "알감자조림", "고추된장무침", "석박지", "매실차/숭늉"], "calorie": 842}
        , {"date": "181221", "type": "B", "menu": ["토마토소스스파게티", "마늘바게트/크림스프", "비엔나채소볶음", "블루베리샐러드*오리엔탈드레싱", "오이피클", "배추김치", "매실차/숭늉"], "calorie": 925}]

    # with open('ssafy.json', "rb") as file:
    #     # 입력 받은 JSON 파일을 불러와 loaded에 저장합니다.
    #     menu = file.read()
    #     menu = menu.decode("cp949")
    # print(menus)

    yearEx = re.compile('[0-9]{2,4}년')
    monthEx = re.compile('[0-9]{1,2}월')
    dateEx = re.compile('[0-9]{1,2}일')
    dayEx = re.compile('[ㄱ-ㅎ가-힣]{1}요일')
    yearAfterTest = re.compile("년\s*뒤")
    monthAfterTest = re.compile("월\s*뒤")
    dayAfterTest = re.compile("일\s*뒤")
    d = datetime.date.today()

    ## 년도 정보 수집. text에 없을 경우 기본값은 현재 년도
    if len(yearEx.findall(text)) == 0:
        yearIn = datetime.date.today().year
    elif len(yearAfterTest.findall(text)) > 0:
        yearIn = datetime.date.today().year
    else:
        yearIn = yearEx.findall(text)[0].replace('년', '')
    ## 월 정보 수집. text에 없을 경우 기본값은 현재 월
    if len(monthEx.findall(text)) == 0:
        monthIn = datetime.date.today().month
    elif len(monthAfterTest.findall(text)) > 0:
        monthIn = datetime.date.today().month
    else:
        monthIn = monthEx.findall(text)[0].replace('월', '')

    ## 일 정보 혹은 요일 정보 수집. text에 없을 경우 기본값은 현재 일
    if len(dateEx.findall(text)) != 0 and len(dayEx.findall(text)) != 0:
        for dateList in dateEx.findall(text):
            if not ('뒤' in dateList) and not ('전' in dateList):
                dateIn = dateEx.findall(text)[0].replace('일', '')
                # dayIn = week.index(dayEx.findall(text)[0][0])
    elif len(dateEx.findall(text)) == 0 and len(dayEx.findall(text)) != 0:
        # keywords.append("정확한 날짜나 요일을 입력해주세요.")
        dateIn = datetime.date.today().day
        # dayIn = week.index(dayEx.findall(text)[0][0])
        #
        # dateIn = datetime.date.today().day
    elif len(dateEx.findall(text)) != 0 and len(dayEx.findall(text)) == 0:
        for dateList in dateEx.findall(text):
            if not ('뒤' in dateList) and not ('전' in dateList):
                dateIn = dateEx.findall(text)[0].replace('일', '')
        # dateIn = dateEx.findall(text)[0].replace('일','')
        # print("/".join([str(monthIn), str(dateIn), str(yearIn)[-2:]]))
        # d = datetime.datetime.strptime("/".join([str(monthIn), str(dateIn), str(yearIn)[-2:]]) , "%m/%d/%y")
        # dayIn = week[d.weekday()]
    else:
        # keywords.append("정확한 날짜나 요일을 입력해주세요.")
        dateIn = datetime.date.today().day
        # dateIn = datetime.date.today().day
        # dayIn = week[now.tm_wday]

    afterEx = re.compile("\d+[일년월]{1}[뒤전]{1}")
    howmuchEx = re.compile("\d+")
    if len(afterEx.findall(text)) != 0:
        afterStr = afterEx.findall(text)[0]
        howmuch = int(howmuchEx.findall(afterStr)[0])
        if '일' in afterStr:
            if '뒤' in afterStr:
                d = d + datetime.timedelta(days=howmuch)
            elif '전' in afterStr:
                d = d - datetime.timedelta(days=howmuch)
        elif '월' in afterStr:
            if '뒤' in afterStr:
                d = d + relativedelta(months=howmuch)
            elif '전' in afterStr:
                d = d - relativedelta(months=howmuch)
        elif '년' in afterStr:
            if '뒤' in afterStr:
                d = d + relativedelta(years=howmuch)
            elif '전' in afterStr:
                d = d - relativedelta(years=howmuch)

    print(d)

    if len(keywords) == 0 and (d.weekday() == 5 or d.weekday() == 6):
        keywords.append("주말에는 밥 안줍니다ㅗ.")
    elif len(keywords) == 0:
        stringTemplate = "%s의 메뉴는 A코스는 %s, B코스는 %s 입니다."
        answer = []
        for menu in menus:
            if menu['date'] == d.strftime('%y%m%d'):
                answer.append(menu)
        if len(answer) == 2:
            # print("4:", stringTemplate % (day_of_month, answer[0]['menu'], answer[1]['menu']))
            keywords.append(stringTemplate % (d.strftime('%d') + '일', answer[0]['menu'], answer[1]['menu']))

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    if len(keywords) == 0:
        return u'%s 일자에 대한 식단 정보가 없는 것 같습니다' % d.strftime('%y/%m/%d')
    else:
        return u'\n'.join(keywords)



# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        # 사주, 영화, 모바일게임 순위, 핫딜, 근처맛집, 싸피식단
        if '운세' in text:
            keywords = _get_text(text)
        elif '영화' in text:
            if '상영' in text:
                # 좋아요순
                if '좋아요' in text:
                    order = "likeCount"
                # 평점순
                elif '평점' in text:
                    order = "point"
                # 개봉순
                else:
                    order = "open"
                keywords = _crawl_naver_keywords(text, order)
            elif '추천' in text:
                keywords = _movie_recommendation(text)
        elif '구글' in text:
            if "도움말" in text:
                keywords = '구글 인기 게임 / 구글 유료 게임 / 구글 게임 매출 순위 / 구글 인기 앱 / 구글 앱 링크'
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
        elif '식단' in text:
            keywords = _crawl_ssafy_keywords(text)
        elif '음악' in text:
            keywords = _crawl_music_keywords(text)
        else:
            keywords = '질문을 이해할 수 없습니다.'
        print("keywords:", keywords)
        if isinstance(keywords, str):
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords
            )
        elif isinstance(keywords, list):
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords[0],  # pretext
                attachments=keywords[1]  # dictionary list
            )
        else:
            for keyword in keywords:
                print(type(keyword))
                if isinstance(keyword, str):
                    sc.api_call(
                        "chat.postMessage",
                        channel=channel,
                        text=keyword
                    )
                else:
                    print('2')
                    sc.api_call(
                        "chat.postMessage",
                        channel=channel,
                        text=keyword[0],  # pretext
                        attachments=keyword[1]  # dictionary list
                    )



        # sc.api_call(
        #     "chat.postMessage",
        #     channel=channel,
        #     text=keywords[0],  # pretext
        #     attachments=keywords[1]  # dictionary list
        # )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
