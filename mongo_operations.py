from utils import get_connection
import requests

# collection=get_connection("manga")['data']

# res=collection.find({},{'_id':0,'chapters':0})


# for manga in res:
#     title=manga['title']
#     print('changing {} ....'.format(str(title)))
#     params={'filter[text]':title}
#     url='https://kitsu.io/api/edge/manga'
#     headers={'Content-Type':'application/json'}
#     response=requests.get(url,params)
#     if response.status_code !=200:
#         print('error')
#         continue
#     try:
#         out=response.json()['data'][0]['attributes']
#     except:
#         print('error')
#         continue
#     update_doc={
#         'release_date': out['startDate'],
#         'end_date':out['endDate'],
#         'description':out['description']
#     }
#     update=collection.update_one({'title':title},{'$set':update_doc})



def extra_info(title='attack on titan'):
    params={'filter[text]':title}
    url='https://kitsu.io/api/edge/manga'
    headers={'Content-Type':'application/json'}
    response=requests.get(url,params)
    if response.status_code !=200:
        print('error')
        return
    try:
        out=response.json()['data'][0]['attributes']
    except:
        print('error')
    update_doc={
        'average_rating':out['averageRating'],
        'popularity_rank':out['popularityRank'],
        'rating_rank':out['ratingRank'],
        'cover':out['coverImage'] if out['coverImage']!=None else out['posterImage']['original'],
        'release_date': out['startDate'],
        'end_date':out['endDate'],
        'description':out['description']
    }
    return update_doc
