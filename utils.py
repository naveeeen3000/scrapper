from pymongo import MongoClient
from decouple import config
import dns
import random
import uuid
import bcrypt


def get_connection(collection_name):
    try:
        client=MongoClient('mongodb+srv://naveen:leomessi10@cluster0.eobif.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
        collection=client['anime_accounts'][collection_name]
        # if collection.acknowledged:
        #     print("Mongo db not connected")
        #     return False
        return {'status':True,'data':collection}
    except:
        return {"status":False,'data':"db connnection failure"}


def update_manga(collection_name):
    coll=get_connection(collection_name)
    

    res=coll.find({},{"_id":0})
    i=0
    for r in res:
        id=uuid.uuid1().hex
        status=coll.update_one(r,{"$set":{"manga_id":id}})
        if status.acknowledged:
            print("changes made...")




def validate_login_creds(data):
    collection=get_connection("users")
    if not collection['status']:
        return {'status':False,'data':'db connection failure'}
    collection=collection['data']
    email=data['email']
    if not email:
        return {'status':False,'data':'email not present'}
    res=collection.find_one({"email":email},{'_id':0})
    if res:
        print("already there............................")
        return {"status":False,'data':"email already registered"}
    if not res:
        salt=bcrypt.gensalt()
        hashed_password=bcrypt.hashpw(str(data['password']).encode('utf-8'),salt)
        data['password']=hashed_password
        return {"status":True,"data":data}


