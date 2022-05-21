import json
from bs4 import BeautifulSoup as bs
import requests
from utils import get_connection
from mongo_operations import extra_info

collection=get_connection('manga')

if not collection['status']:
    print(collection['data'])
    exit()

collection=collection['data']

def scrapper():
    pages=767
    base_url='http://mangapanda.in/popular-manga?page='
    for i in range(1,pages+1):
        url=base_url+str(i)
        page=requests.get(url)
        soap=bs(page.content,'html.parser')
        try:
            div=soap.find_all(class_='cate-manga')[0]
            div2=div.find_all(class_='col-md-6')
            for d in div2:
                manga_href=d.a.attrs['href']
                manga=magna_details(manga_href)
                if manga['status']=='abort':
                    print('manga chapters already exist')
                    break
                elif manga['status']=='update':
                    if update_db(manga['manga_details']):
                        print("Updated to db...")
                elif manga['status']=='create':
                    write_to_db(manga['manga_details'])
        except:
            print("PAGE ERROR!")


def magna_details(url):

    page=requests.get(url)
    status=''
    soap=bs(page.content,"html.parser")
    manga_exists=False
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
    title=title.split('Manga')[0]
    check=list(collection.find_one({'title':title}))
    if len(check)!=0:
        manga_exists=True
    manga_details['title']=title
    manga_details['alternative']=alternative
    manga_details['author']=author
    manga_details['genre']=genre
    manga_details['status']=status.strip(' ')
    print("downloading {} ".format(str(title)))
    chapter_list_div=soap.find_all(class_='chapter-list')[1]
    lis=chapter_list_div.ul.find_all('li')
    chapters=[]
    chapter_one_href=lis[0].div.h4.a.attrs['href']
    chapter_one=requests.get(chapter_one_href)
    if 'manganato' in chapter_one.url and manga_exists:
        chapters=download_manganato_chapters(lis)
        status='update'
    elif 'manganato' in chapter_one.url and not manga_exists:
        chapters=download_manganato_chapters(lis)
        status='create'
    elif 'manganato' not in chapter_one.url and not manga_exists:
        extras=extra_info(title)
        manga_details['average_rating']=extras['average_rating']
        manga_details['popularity_rank']=extras['popularity_rank']
        manga_details['rating_rank']=extras['rating_rank']
        manga_details['cover']=extras['cover']
        manga_details['release_date']=extras['release_date']
        manga_details['end_date']=extras['end_date']
        manga_details['description']=extras['description']
        chapters=download_mangapanda_chapters(lis)
        status='create'
    else:
        return {'status':'abort'}

    manga_details['chapters']=chapters
    return {'manga_details':manga_details,'status':status}

def download_manganato_chapters(lis):
    chapters=[]
    for li in lis:
        href=li.div.h4.a.attrs['href']
        print('downloading {}'.format(str(li.div.h4.a.contents[0])))
        chapter_image_list=Manganato_download_images(href)
        chapters.append({li.div.h4.a.contents[0]:chapter_image_list})
    return chapters


def Manganato_download_images(href):
    chapter_list=[]
    try:
        page=requests.get(href)
        soap=bs(page.content,'html.parser')
        p=soap.find_all(id='arraydata')[0].contents[0]
        chapter_list=p.split(',')
        return chapter_list
    except:
        chapter_list=["chapter doesn\'t exist"]



def download_mangapanda_chapters(lis):
    chapters=[]
    for li in lis:
        href=li.div.h4.a.attrs['href']
        print('downloading {}'.format(str(li.div.h4.a.contents[0])))
        chapter_image_list=download_mangapanda_images(href)
        chapters.append({li.div.h4.a.contents[0]:chapter_image_list})
    return chapters

def download_mangapanda_images(url):
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
    


def update_db(manga):
    print('updating {} to db....'.format(str(manga['title'])))
    try:
        updated_chapter_list={'$set':{'chapters':manga['chapters']}}
        res=collection.update_one({'title':manga['title']},updated_chapter_list)
        return True
    except:
        return False


def write_to_db(manga):
    try:
        res=collection.insert_one(manga)
        if res.acknowledged:
            print(manga['title']+'inserted to db./////')
    except:
        print('not inserted')

    

scrapper()