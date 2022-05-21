from utils import get_connection
import requests

collection=get_connection("manga")['data']
# print(collection)
res=collection.find({},{'_id':0,'chapters':0})

# print(list(res))

for manga in res:
    title=manga['title']
    print('changing {} ....'.format(str(title)))
    params={'filter[text]':title}
    url='https://kitsu.io/api/edge/manga'
    headers={'Content-Type':'application/json'}
    response=requests.get(url,params)
    out=response.json()['data'][0]['attributes']
    update_doc={
    'title':title.split('Manga')[0],
    'cover':out['coverImage'] if out['coverImage']!= None else out['posterImage']['original'],
    'rating_rank':out['ratingRank'],
    'popularity_rank':out['popularityRank'],
    'average_rating':out['averageRating']
    }
    update=collection.update_one({'title':title},{'$set':update_doc})