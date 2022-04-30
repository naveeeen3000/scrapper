from bs4 import BeautifulSoup as bs
import time
import requests
import random
base_url="https://manganato.com/"
import json

def get_manga_hrefs(i):
    print("generating manga hrefs.....")
    page=requests.get(base_url+"genre-all/"+str(i)+"/")
    
    
    
    soup=bs(page.content,"html.parser")

    manga_list_div=soup.find_all(class_='content-genres-item')


    # name=manga_list_div[0].h3.a.contents[0]
    href=[ manga.a.attrs['href'] for manga in manga_list_div]
    # individual_manga_pages.append(href)
    # individual_manga_pages.
    return href


def get_manga(manga_hrefs):
    print("getting manga details.......")
    manga_details={}
    url=manga_hrefs
    page=requests.get(url)
    soup=bs(page.content,"html.parser")
    manga_info=soup.find_all(class_='story-info-right')[0]
    chapter_list_div=soup.find_all(class_='row-content-chapter')[0]
    name=manga_info.h1.contents[0]
    table=manga_info.table.tbody.find_all('tr')
    for tr in table:
        key=tr.find_all('td')[0].contents[1].split(":")[0]
        key=key.split(" ")[0]
        if key=="Author(s)":
            manga_details[key]=tr.find_all(class_='table-value')[0].a.contents[0]
        if key=='Genres':
            val=[author.contents[0] for author in tr.find_all('td')[1].find_all('a')]
            manga_details[key]=val
        if key=='status':
            val=tr.find_all('td')[1].contents[0]
            manga_details[key]=val
    right_extent=manga_info.div
    updated_at=right_extent.find_all('p')[0].find_all('span')[1].contents[0]
    chapter_list={}
    for chapter in chapter_list_div.find_all('li'):
        chapter_list[chapter.a.contents[0]]=chapter.a.attrs['href']
    description=soup.find_all(class_='panel-story-info-description')[0].contents[2]
    manga_details['title']=name
    manga_details['updated']=updated_at
    manga_details['description']=description
    manga_details['chapters']=chapter_list
    return manga_details

def download_manga_images(manga_details):
    manga_chapters={}
    print("Downloading manga.....")
    chapter_list=manga_details['chapters']
    i=1
    for key,value in chapter_list.items():
        print("downloading chapter ",i)
        manga_chapters[key]=download_manga(value)['manga_list']
        i+=1
    return manga_chapters

def download_manga(chapter):
    manga_chapters_list=[]
    page=requests.get(chapter)
    soup=bs(page.content,'html.parser')
    manga_chapters_hrefs={}
    chapter_name=soup.find_all(class_='panel-chapter-info-top')[0].h1.contents[0]
    # print(chapter_name)
    chapters=soup.find_all(class_='container-chapter-reader')[0].find_all('img')
    for img_tag in chapters:
        href=img_tag.attrs['src']
        manga_chapters_list.append(href)
        manga_chapters_hrefs[img_tag.attrs['title'].split("MangaNato")[0]]=href
    manga_chapters={chapter_name:manga_chapters_hrefs}
    return {'manga_list':manga_chapters_list,'manga_dict':manga_chapters}


def main():
    pages=1
    hrefs=[]
    mangas=[]
    # print(get_manga_hrefs(1))
    for i in range(1,pages+1):
        hrefs+=get_manga_hrefs(i)
    
    # for href in hrefs:
    manga_details=get_manga(hrefs[0])
    manga_chapters=download_manga_images(manga_details)
    manga_details['chapters']=manga_chapters
    mangas.append(manga_details)
    dump=json.dumps({'data':mangas},indent=4)
    with open("data.json",'w') as file:
        file.write(dump)


main()