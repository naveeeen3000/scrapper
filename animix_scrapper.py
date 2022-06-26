import json
from bs4 import BeautifulSoup as bs
import requests 
from pymongo import MongoClient
from utils import get_connection

BASE_URL='https://animepahe.org'

def anime_all(url):
    page=requests.get(url)
    soap=bs(page.content,'html.parser')
    div=soap.find_all(class_='tab-content')[0]
    all_divs=div.find_all(class_='tab-pane fade')
    for d in all_divs:
        get_anime_href(d)
        

def get_anime_href(div):
    row=div.find_all(class_='col-12 col-md-6')
    for r in row:
        get_anime_info(r.a.attrs['href'])
        print("done....")
        

def get_anime_info(url):
    anime_details={}
    page=requests.get(BASE_URL+url)
    print(BASE_URL+url)
    soap=bs(page.content,'html.parser')
    poster_image=soap.find_all(class_='anime-poster')[0].img.attrs['data-src']
    title=soap.find_all('h1')[0].span.contents[0]
    print("downloading {} ............".format(title))
    japanese_title=soap.find_all(class_='japanese')[0].contents[0]
    summary=soap.find_all(class_="anime-synopsis")[0].contents[0]
    anime_info=soap.find_all(class_="anime-info")[0].find_all('p')
    for p in anime_info:
        if p.a != None:
            anime_details[p.strong.contents[0].split(':')[0]]=p.a.contents[0]
        else:
            anime_details[p.strong.contents[0].split(':')[0]]=p.contents[len(p.contents)-1].replace('\n','')
    anime_genre=[]
    genre=soap.find_all(class_="anime-genre")[0].find_all('li')
    for li in genre:
        anime_genre.append(li.a.contents[0])
    
    anime_details['title']=title
    anime_details['japanese_title']=japanese_title
    anime_details['synopsis']=summary
    anime_details['genre']=anime_genre

    anime_relation=soap.find(class_="anime-relation")
    if anime_relation!=None:
        section=anime_relation.find_all(class_='col-12 col-sm-6')
        
        h4s=anime_relation.find_all('h4')
        
        for sec in section:
            anime_details[sec.h4.span.contents[0].lower().replace(" ","_")]=[ h5.a.contents[0] for h5 in sec.find_all('h5')]

    anime_recomendation=soap.find(class_='anime-recommendation')
    if anime_recomendation!=None:
        recomm_section=anime_recomendation.find_all(class_='col-12 col-sm-6 mb-3')
        anime_details['recommendation']=[ sec.h5.a.contents[0] for sec in recomm_section]

    write_to_db(anime_details)

def write_to_db(anime_deatils):
    coll=get_connection('anime')
    if not coll['status']:
        print('db connection failure')
    else:
        coll=coll['data']
        res=coll.insert_one(anime_deatils)
        if res.acknowledged:
            print("{} inserted to db!!".format(anime_deatils['title']))
        else:
            print("Insertion failure :( ")

anime_all("https://animepahe.org/anime")