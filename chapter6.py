# インタラクティブダッシュボードを作成する

#ライブラリをインポートする
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk    #３Dグラフ表示のために必要
import plotly.express as px
import glob


#タイトルを設定する
st.title("日本の賃金ダッシュボード")

#データを読み込む
# see csv data in folder.
files = glob.glob("../data/雇用*.csv")

df_all_ind = pd.read_csv(files[0],encoding = "shift-jis")
df_all_category = pd.read_csv(files[1],encoding = "shift-jis")
df_pref_ind = pd.read_csv(files[2],encoding = "shift-jis")

###都道府県別１人あたり平均賃金を日本地図にヒートマップ表示する###

#set header
st.header("■2019年：１人あたりの平均賃金のヒートマップ")

#read lat_lon data for city
jp_lat_lon = pd.read_csv("../data/pref_lat_lon.csv")

#rename columns(display)
jp_lat_lon = jp_lat_lon.rename(columns = {"pref_name":"都道府県名"})

#filter data as agesum and 2019(display)
df_pref_temp = df_pref_ind.loc[(df_pref_ind["年齢"]=="年齢計")&(df_pref_ind["集計年"]==2019)]

#merge data on prefecture
df_pref_map = pd.merge(df_pref_temp,jp_lat_lon, on = "都道府県名")

#normalization
df_pref_map["一人あたり賃金（相対値）"] = (df_pref_map["一人当たり賃金（万円）"]-df_pref_map["一人当たり賃金（万円）"].min())/(df_pref_map["一人当たり賃金（万円）"].max()-df_pref_map["一人当たり賃金（万円）"].min())

#集計年別の一人あたり平均賃金の推移をグラフ表示#pydeckを使って可視化する

#①set view (central setting as Tokyo)
view = pdk.ViewState(
    longitude=139.691648,
    latitude = 35.689185,
    zoom = 4,
    pitch = 40.5,
)

#②set layer(graph type setting)
layer = pdk.Layer(
    "HeatmapLayer",
    data = df_pref_map,
    opacity=0.4,#不透明度
    get_position = ["lon","lat"],
    threshold = 0.3,#閾値
    get_weight = "一人あたり賃金（相対値）",
)

#③set deck
layer_map = pdk.Deck(
    layers=layer,
    initial_view_state=view,
)
#④set streamlit
st.pydeck_chart(layer_map)

#チェックボックスがONの場合にデータを表示させる
show_df = st.checkbox("Show DataFrame")
if show_df == True:
    st.write(df_pref_map)


###集権年別の一人当たりの平均賃金の推移をグラフ表示する###
###全国の平均賃金の推移と都道府県ごとの平均賃金の推移を乗せる###

st.header("■集計年別の一人当たり賃金（万円）の推移")

#prepare data
df_ts_mean = df_all_ind.loc[df_all_ind["年齢"]=="年齢計"]
df_ts_mean = df_ts_mean.rename(columns={"一人当たり賃金（万円）":"全国_一人当たり賃金（万円）"})

df_pref_mean = df_pref_ind.loc[df_pref_ind["年齢"]=="年齢計"]

#select box list
pref_list = df_pref_mean["都道府県名"].unique()

option_pref = st.selectbox(
    "都道府県",
    (pref_list)
)


#filter data 
df_pref_mean = df_pref_mean.loc[df_pref_mean["都道府県名"]==option_pref]

#merge data 
df_mean_line = pd.merge(df_ts_mean,df_pref_mean,on=["集計年"])

#select columns
df_mean_line = df_mean_line[["集計年","全国_一人当たり賃金（万円）","一人当たり賃金（万円）"]]

#set index
df_mean_line = df_mean_line.set_index("集計年")
df_mean_line
#view line chartst
st.line_chart(df_mean_line)


###年齢階級別の全国一人あたり平均賃金をバブルチャート表示###

#header
st.header("■年齢階級別の全国一人当たり平均賃金（万円）")

#prepare data
df_mean_bubble = df_all_ind.loc[df_all_ind["年齢"]!="年齢計"]

#x: 一人当たり賃金　y: 　年間賞与そのた特別供与額　size:　所定内給与
fig = px.scatter(df_mean_bubble,
    x="一人当たり賃金（万円）",
    y="年間賞与その他特別給与額（万円）",
    range_x = [150,700],
    range_y = [0,150],
    size = "所定内給与額（万円）",
    size_max = 38,
    color="年齢",
    animation_frame="集計年",
    animation_group="年齢"
)

st.plotly_chart(fig)

###産業別の平均賃金を横棒グラフ表示###

st.header("■産業別の賃金推移")

year_list = df_all_category["集計年"].unique()
option_year = st.selectbox(
    "集計年",
    (year_list)
)

wage_list = ["一人当たり賃金（万円）","所定内給与額（万円）","年間賞与その他特別給与額（万円）"]
option_wage = st.selectbox(
    "賃金の種類",
    (wage_list)
)

df_mean_categ = df_all_category.loc[df_all_category["集計年"]==option_year]

max_x = df_mean_categ[option_wage].max() + 50

fig = px.bar(df_mean_categ,
    x=option_wage,
    y="産業大分類名",
    color="産業大分類名",
    animation_frame = "年齢",
    range_x = [0,max_x],
    orientation = 'h',#横向きにする
    width = 800,
    height = 500,
)

st.plotly_chart(fig)

st.text("出展：RESAS(地域経済分析システム）")
st.text("本結果はRESAS（値維持経済分析システム）を加工して作成")

#利用するオープンデータの利用規約は必ず読むべし。