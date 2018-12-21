import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

## 사용자(userId)의 영화(movieId)에 대한 평가(rating) 데이터. userid, movieId, rating(1~5), timestamp 로 구성
ratings_data = pd.read_csv("C:\\Users\\student\\PycharmProjects\\myChatbot\\ml-latest-small\\ratings.csv")
# print(ratings_data.columns.tolist())
## 영화데이터. movieId, title, genres로 구성
## 추천 시스템을 content-based Filtering으로 구성하기 위해서는 아래 dataset의 genres를 이용해야 한다.
movie_names = pd.read_csv("C:\\Users\\student\\PycharmProjects\\myChatbot\\ml-latest-small\\movies.csv")
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

title_particle = 'Iron Man'
keywords = []
## 정확한 영화의 제목을 알고 있을 경우
if title_particle in movie_names_df['title'].values.tolist():
    e = {}
    print('There is exact movie')
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
    keywords.append(e)
## 정확한 영화의 제목을 모르고 일부분만 알고 있을 경우
## df[df['title'].str.contains("hello")]
else:
    print('There is no exact movie')

    possible_titles = movie_names_df[movie_names_df['title'].str.contains(title_particle)]['title'].values
    for title in possible_titles.tolist():
        e = {}
        ratings = user_movie_rating[str(title)]
        movies_like_this = user_movie_rating.corrwith(ratings)
        corr_rate = pd.DataFrame(movies_like_this, columns=['Correlation'])
        corr_rate.dropna(inplace=True)

        corr = corr_rate.join(ratings_mean_count['rating_counts'])

        print("Movies like ", title + ":")
        print(list(corr.index))
        print(corr[(corr['rating_counts'] > 50)].sort_values('Correlation', ascending=False).head())

        corrlist = []
        for row in corr[(corr['rating_counts'] > 50)].sort_values('Correlation', ascending=False).head(10).iterrows():
            index, data = row
            rowtolist = [index, data.tolist()]
            corrlist.append(rowtolist)
        e['title'] = title_particle
        e['corr'] = corrlist
        keywords.append(e)


for keyword,i in enumerate(keywords):
    print(i,":",keyword)

# forrest_gump_ratings = user_movie_rating[user_movie_rating['title'].str.contains(title)]
# print(forrest_gump_ratings)

# # print(forrest_gump_ratings.head())
#
# movies_like_forest_gump = user_movie_rating.corrwith(forrest_gump_ratings)
#
# corr_forrest_gump = pd.DataFrame(movies_like_forest_gump, columns=['Correlation'])
# corr_forrest_gump.dropna(inplace=True)
# # print(corr_forrest_gump.head())
# print(corr_forrest_gump.sort_values(by='Correlation', ascending=False).head())