import time
import datetime
import re
from dateutil.relativedelta import relativedelta

#
text = "20일에서 4일뒤"
keywords = []

now = time.localtime()
week = ('월', '화', '수', '목', '금', '토', '일')

# with open('ssafy.json', "rb") as file:
#     # 입력 받은 JSON 파일을 불러와 loaded에 저장합니다.
#     menu = file.read()
#     menu = menu.decode("cp949")
# print(menus)

menus = [
    {"date": "19", "type": "A", "menu": ["콩나물밥*양념장", "된장찌개", "떡갈비조림", "가지나물", "치커리유자청무침", "배추김치", "수정과/숭늉"],
     "calorie": 1114}
    , {"date": "19", "type": "B", "menu": ["홍합짬뽕", "MINI쌀밥", "만두탕수", "스크램블에그", "단무지무침", "배추김치", "수정과/숭늉"],
       "calorie": 1041}
    , {"date": "20", "type": "A", "menu": ["경상도식고깃국", "강낭콩밥*쌀밥", "깻잎해물전", "탕평채", "건파래볶음", "석박지", "미숫가루/숭늉"],
       "calorie": 765}
    , {"date": "20", "type": "B", "menu": ["마파두부덮밥", "만가닥맑은국", "꼬마돈가스*케찹", "콩나물겨자채무침", "콘버터구이", "배추김치", "미숫가루/숭늉"],
       "calorie": 1202}
    , {"date": "21", "type": "A", "menu": ["순대국밥", "잡곡밥*쌀밥", "김치전", "알감자조림", "고추된장무침", "석박지", "매실차/숭늉"], "calorie": 842}
    , {"date": "21", "type": "B",
       "menu": ["토마토소스스파게티", "마늘바게트/크림스프", "비엔나채소볶음", "블루베리샐러드*오리엔탈드레싱", "오이피클", "배추김치", "매실차/숭늉"], "calorie": 925}]

yearEx = re.compile('[0-9]{2,4}년')
monthEx = re.compile('[0-9]{1,2}월')
dateEx = re.compile('[0-9]{1,2}일')
dayEx = re.compile('[ㄱ-ㅎ가-힣]{1}요일')
yearAfterTest = re.compile("년\s*뒤")
monthAfterTest = re.compile("월\s*뒤")
dayAfterTest = re.compile("일\s*뒤")
d = datetime.date.today()

## 년도 정보 수집. text에 없을 경우 기본값은 현재 년도
if len(yearEx.findall(text)) == 0 :
    yearIn = datetime.date.today().year
elif len(yearAfterTest.findall(text)) > 0:
    yearIn = datetime.date.today().year
else:
    yearIn = yearEx.findall(text)[0].replace('년','')
## 월 정보 수집. text에 없을 경우 기본값은 현재 월
if len(monthEx.findall(text)) == 0:
    monthIn = datetime.date.today().month
elif len(monthAfterTest.findall(text)) > 0:
    monthIn = datetime.date.today().month
else:
    monthIn = monthEx.findall(text)[0].replace('월','')

## 일 정보 혹은 요일 정보 수집. text에 없을 경우 기본값은 현재 일
if len(dateEx.findall(text)) != 0 and len(dayEx.findall(text)) != 0:
    for dateList in dateEx.findall(text):
        if not('뒤' in dateList) and not('전' in  dateList):
            dateIn = dateEx.findall(text)[0].replace('일','')
            # dayIn = week.index(dayEx.findall(text)[0][0])
elif len(dateEx.findall(text)) == 0 and len(dayEx.findall(text)) != 0:
    keywords.append("정확한 날짜나 요일을 입력해주세요.")
    # dayIn = week.index(dayEx.findall(text)[0][0])
    #
    # dateIn = datetime.date.today().day
elif len(dateEx.findall(text)) != 0 and len(dayEx.findall(text)) == 0:
    for dateList in dateEx.findall(text):
        if not('뒤' in dateList) and not('전' in  dateList):
            dateIn = dateEx.findall(text)[0].replace('일','')
    # dateIn = dateEx.findall(text)[0].replace('일','')
    # print("/".join([str(monthIn), str(dateIn), str(yearIn)[-2:]]))
    # d = datetime.datetime.strptime("/".join([str(monthIn), str(dateIn), str(yearIn)[-2:]]) , "%m/%d/%y")
    # dayIn = week[d.weekday()]
else:
    keywords.append("정확한 날짜나 요일을 입력해주세요.")
    # dateIn = datetime.date.today().day
    # dayIn = week[now.tm_wday]



afterEx = re.compile("\d+[일년월]{1}뒤")
howmuchEx = re.compile("\d+")
if len(afterEx.findall(text)) != 0:
    afterStr = afterEx.findall(text)[0]
    howmuch = int(howmuchEx.findall(afterStr)[0])
    if '일' in afterStr:
        d = d+datetime.timedelta(days=howmuch)
    elif '월' in afterStr:
        d = d + relativedelta(months=howmuch)
    elif '년' in afterStr:
        d = d + relativedelta(years=howmuch)

print(d)


if len(keywords) == 0 and (d.weekday() == 5 or d.weekday() == 6):
    keywords.append("주말에는 밥 안줍니다ㅗ.")
elif len(keywords) == 0:
    stringTemplate = "%s의 메뉴는 A코스는 %s, B코스는 %s 입니다."
    answer = []
    for menu in menus:
        if menu['date'] == d.strftime('%d'):
            answer.append(menu)
    if len(answer) == 2:
        # print("4:", stringTemplate % (day_of_month, answer[0]['menu'], answer[1]['menu']))
        keywords.append(stringTemplate % (d.strftime('%d')+'일', answer[0]['menu'], answer[1]['menu']))

if len(keywords) == 0:
    print('%s 일자에 대한 식단 정보가 없는 것 같습니다' % d.strftime('%y/%m/%d'))
else:
    print(u'\n'.join(keywords))

