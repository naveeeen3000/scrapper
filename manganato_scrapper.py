from gc import collect
import json
from turtle import update
from bs4 import BeautifulSoup as bs
import requests
from utils import get_connection




def scrapper():
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
            manga_href=d.a.attrs['href']
            manga=magna_details(manga_href)
            if not manga:
                break
            if update_db(manga):
                print('db updated...')



def update_db(manga):
    print('updating {} to db....'.format(str(manga['title'])))
    coll=get_connection('manga')
    if not coll['status']:
        return {"status":coll['data']}
    coll=coll['data']
    try:
        updated_chapter_list={'$set':{'chapters':manga['chapters']}}
        res=coll.update_one({'title':manga['title']},updated_chapter_list)
        print('updated to db.......')
        return True
    except:
        return False


def magna_details(url):

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
    genre=[ g.contents[0].strip(' ') for g in genre[:-2] ]
    status=contents[-7]
    manga_details['title']=title
    manga_details['alternative']=alternative
    manga_details['author']=author
    manga_details['genre']=genre
    manga_details['status']=status.strip(' ')

    chapter_list_div=soap.find_all(class_='chapter-list')[1]
    lis=chapter_list_div.ul.find_all('li')
    chapters=[]
    for li in lis:
        href=li.div.h4.a.attrs['href']
        chapter_image_list=download_images(href)
        if not chapter_image_list:
            return False
        chapters.append({li.div.h4.a.contents[0]:chapter_image_list})
    manga_details['chapters']=chapters
    return manga_details


def download_images(url="http://mangapanda.in/attack-on-titan-chapter-139.5"):
    # chapter_list=[]
    try:
        page=requests.get(url)
        soap=bs(page.content,'html.parser')
        if 'manganatos' in page.url:
            print('downloading chapter....')
            return Manganato_download_images(soap)
        else:
            return False
    except:
        chapter_list=['chapter doesn\'t exist']
    return chapter_list
    
def Manganato_download_images(soap):
    chapter_list=[]
    try:
        p=soap.find_all(id='arraydata')[0].contents[0]
        chapter_list=p.split(',')
        # print(chapter_list)
        return chapter_list
    except:
        chapter_list=["chapter doesn\'t exist"]

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

    

bleach=magna_details(url='http://mangapanda.in/manga/attack-on-titan')
print(bleach)
if update_db(bleach):
    print('yessss')