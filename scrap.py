from operator import truediv
from bs4 import BeautifulSoup as bs
import requests

url="https://kissmanga.org"


def get_manga_hrefs(i=1,base_url="https://kissmanga.org/"):
    url=base_url+"manga_list?page="+str(i)
    
    page=requests.get(url)
    soup=bs(page.content,'html.parser')
    mangas=soup.find_all(class_='item_movies_in_cat')
    href=[base_url+manga.div.a.attrs['href'] for manga in mangas]
    return href
    


def get_manga_details(href):
    page=requests.get(href)
    soup=bs(page,'html.parser')
    name=soup.find_all(class_='bigChar')[0].contents[0]
    info=soup.find_all(class_='barContent full')[0].find_all(class_='full')[0].find_all('p')
    manga_info={'name':name}
    for p in info:
        key=p.span.contents[0]
        value=[ a.contents[0] for a in p.find_all('a')]
        manga_info[key]=value
    manga_info['summary']=soup.find_all(class_='summary')[0].p.contents[0]
    chapter_list=soup.find_all(class_='listing listing8515 full')[0].find_all('div')
    chapter_list=chapter_list[1:]
    chapters=[ chapter.div.h3.a.attrs['href'] for chapter in chapter_list]
    manga_info['chapters']=chapters
    print(manga_info)
    return manga_info


print(get_manga_hrefs(i=1,base_url=url))

# get_manga_details(get_manga_hrefs(i=2,base_url=url)[0])


