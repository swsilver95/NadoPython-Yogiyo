import pandas as pd
import requests
import json
import urllib.parse as par
import streamlit as st
import pydeck as pdk

st.write("# 요기요 가게 검색")
user_input = st.text_input("원하는 주소 입력 >> ")
encoded = par.quote(user_input)
header = {
'accept': 'application/json, text/plain, */*',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
'origin': 'https://www.yogiyo.co.kr',
'referer': 'https://www.yogiyo.co.kr/',
'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Whale";v="3"',
'sec-ch-ua-mobile': '?0',
'sec-ch-ua-platform': 'macOS',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-site',
'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.57 Whale/3.14.133.23 Safari/537.36',
'x-api-key': 'OAYAUiAAxt8hQdAtt9sCCDHwjqxDaev8l4EJBbJ2',
}
url = f"https://adiyo.yogiyo.co.kr/geocode/?lat=37.5076977316442&lng=127.104009232191&query={encoded}"
address_data = requests.get(url, headers=header)
address_data = json.loads(address_data.text)
num = 1
coord_list = []
address_list = []
for item in address_data["items"]:
    # st.write(f"{num} >> {item['law']['sido']} {item['law']['sigugun']} {item['law']['dongmyun']} {item['law']['detail']}")
    address_list.append(f"{item['law']['sido']} {item['law']['sigugun']} {item['law']['dongmyun']} {item['law']['detail']}")
    coord_list.append([item['point']['lat'], item['point']['lng']])
    num += 1
option = st.selectbox('원하는 주소 선택 >> ', address_list)
menu = address_list.index(option)
# menu = int(st.text_input("원하는 주소 선택 >> "))
user_coord = coord_list[menu]

price_limit = st.slider("배달 요금 선택 (x 원 이하) >> ", min_value=0, max_value=10000, step=500)


# 가게 데이터 가져오기
headers = {
'referer': 'https://www.yogiyo.co.kr/mobile/',
'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
'sec-ch-ua-mobile': '?0',
'sec-ch-ua-platform': 'macOS',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-origin',
'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
'x-apikey': 'iphoneap',
'x-apisecret': 'fe5183cc3dea12bd0ce299cf110a75a2',
}
df = pd.DataFrame()
for page_num in range(1):
    data = requests.get(f"https://www.yogiyo.co.kr/api/v1/restaurants-geo/?items=60&lat={user_coord[0]}&lng={user_coord[1]}&order=rank&page={page_num}&search=", headers=headers)
    result = json.loads(data.text) # json --> 딕셔너리
    store_list = result["restaurants"]
    for store in store_list:
        if int(store['adjusted_delivery_fee']) > price_limit:
            continue
        # st.write(f"가게 이름 : {store['name']}")
        # st.write(f"배달 요금 : {store['adjusted_delivery_fee']}")
        # st.write(f"리뷰 수 : {store['review_count']}")
        # st.write(f"별점 : {store['review_avg']}")
        # st.write("-----------------------------------------")
        df = df.append({"가게이름": store['name'], "배달요금": store['adjusted_delivery_fee'], "리뷰수": store['review_count'], "별점": store['review_avg'], "lat":store['lat'], "lng":store['lng']}, ignore_index=True)

layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position="[lng, lat]",
    get_radius=60,
    get_fill_color="[255, 255, 255]",
    pickable=True
)
lat_center = df["lat"].mean()
lon_center = df["lng"].mean()
initial = pdk.ViewState(latitude=lat_center, longitude=lon_center, zoom=10)

map = pdk.Deck(layers=[layer], initial_view_state=initial,
               tooltip={
                   "html": "가게이름 : {가게이름}<br/>배달요금 : {배달요금}<br/>별점 : {별점}<br/>리뷰 수 : {리뷰수}",
                   "style": {"color":"white"}
               })
st.pydeck_chart(map)