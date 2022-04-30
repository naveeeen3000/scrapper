import json
from bs4 import BeautifulSoup as bs
import bs4
import requests
from utils import get_connection




def get_page_urls():
    pages=767
    # href=[]
    base_url='http://mangapanda.in/popular-manga?page='
    for i in range(1,pages+1):
        print('\n on page {} \n'.format(i))    
        url=base_url+str(i)


        page=requests.get(url)
    
        soap=bs(page.content,'html.parser')
    
        div=soap.find_all(class_='cate-manga')[0]

        div2=div.find_all(class_='col-md-6')

        for d in div2:
            magna_details(d.a.attrs['href'])
    # print(href)


def magna_details(url="http://mangapanda.in/manga/the-unsuccessful-yet-academically-unparalleled-sage-a-cheating-s-rank-sorcerers-post-rebirth-adventurer-log"):

    page=requests.get(url)

    soap=bs(page.content,"html.parser")

    manga_details={}
    info_div=soap.find_all(class_='media manga-detail')[0]

    manga_details['cover_image']=soap.find_all(class_='media-left cover-detail')[0].img.attrs['src']

    title=info_div.find_all('div')[1].h1.contents[0]
    some=info_div.find_all('div')[1].p.find_all('span')
    contents=info_div.find_all('div')[1].p.contents
    alternative=contents[2]
    author=contents[10]
    genre=info_div.find_all('div')[1].p.find_all('a')
    genre=[ g.contents[0] for g in genre[:-2] ]
    status=contents[-7]

    manga_details['title']=title
    manga_details['alternative']=alternative
    manga_details['author']=author
    manga_details['genre']=genre
    manga_details['status']=status.strip(' ')

    chapter_list_div=soap.find_all(class_='chapter-list')[1]
    lis=chapter_list_div.ul.find_all('li')
    # print(lis[0].div.h4.a)
    print(manga_details)
    chapters=[ {li.div.h4.a.contents[0] : download_images(li.div.h4.a.attrs['href'])} for li in lis]
    manga_details['chapters']=chapters
    write_to_db(manga_details)
    # write_to_json(manga_details)
    print('process completed.........')


def download_images(url):
    chapter_list=[]
    try:
        page=requests.get(url)
        print('downloading chapter....')
        soap=bs(page.content,'html.parser')
        
        # print(soap)
        selector_div=soap.find_all(class_='chapter-content-inner text-center image-auto')[0]
        p=selector_div.p.contents[0]
        chapter_list=p.split(",")
    except:
        chapter_list=['chapter doesn\'t exist']
    return chapter_list
    
    

def write_to_db(manga):
    
    coll=get_connection('manga')
    if not coll['status']:
        return {"status":coll['data']}
    coll=coll['data']
    
    try:
        res=coll.insert_one(manga)
        print(manga['title']+'inserted to db./////')
    except:
        print('not inserted')

    

get_page_urls()

# magna_details()