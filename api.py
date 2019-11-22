# @author Abhay Rastogi ,Shubham Rajput


from aiohttp import web
import bson.json_util  as json_util
import json
import pymongo
import aiohttp_cors


from bson.objectid import ObjectId
mongourl = "mongodb://localhost:27017/"


def insertUser(jsn,col):
    # d_type == 'teacher' or d_type == 'student' or d_type == 'admin' or d_type == 'cleaner' or d_type == 'parent' or d_type == 'guardian'
    myclient = pymongo.MongoClient(mongourl)
    mydb = myclient["creaxt"]  # Database Name
    mycol = mydb[col] # Database Name
    id = ObjectId()
    d_type = jsn['type']
    if d_type !='principal' :
        print("notprincipal")

        conv_id = {**jsn, **{"UID": str(id), "_id": id}}
        data = conv_id
        x =  mycol.insert_one(data)

        ids = {"_id":ObjectId(jsn['UID'])}
        newvalues = {'$push': {jsn['type']:id}}
        mycol.update_one(ids, newvalues)

        return x


    else:

        print("principalcreated")

        conv_id ={**jsn,**{"UID":str(id),"_id": id } }
        data =  conv_id
        print(data)
        return mycol.insert_one(data)

def insertActivty(jsn,col):
    d_type = jsn['type']
    print("activity")
    myclient = pymongo.MongoClient(mongourl)
    mydb = myclient["creaxt"]  # Database Name
    mycol = mydb[col]  # Database Name
    id = ObjectId()

    conv_id = {**jsn, **{"UID": str(id), "_id": id}}
    data = conv_id
    x = mycol.insert_one(data)

    myclientuser = pymongo.MongoClient(mongourl)
    mydbuser = myclientuser["creaxt"]
    myuser = mydbuser['user']
    ids = {"_id": ObjectId(jsn['CID'])}
    newvalues = {'$push': {jsn['type']: id}}
    myuser.update_one(ids, newvalues)
    return x

async def create(request):
    try:
        collection = request.match_info.get('collection', "Anonymous")

        # myclient = pymongo.MongoClient(mongourl)
        # mydb = myclient["creaxt"]  # Database Name
        # mycol = mydb[collection]  # Collection name
        j = await request.json()

        if collection == 'user':
           x =  insertUser(j,collection)
        else:
           x =  insertActivty(j,collection)

        # x = mycol.insert_one(j)
        # print(x.inserted_id)
        response_obj = {'status': 'success',"_id":str(x.inserted_id)}
        # response_obj = {'status': 'success', "_id":"ok"}
        return web.Response(text=json.dumps(response_obj), status=200)

    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        web.Response(text=json.dumps(response_obj), status=500)





async def show(request):
    try:
        collection = request.match_info.get('collection', "Anonymous")
        print(collection)
        myclient = pymongo.MongoClient(mongourl)
        mydb = myclient["creaxt"]  # Database Name
        mycol = mydb[collection]  # Collection name
        mydoc = list(mycol.find())  # add all data in a List
        # convert list into json
        response_obj = json.loads(json_util.dumps(mydoc))
        return web.Response(text=json.dumps(response_obj), status=200)

    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        web.Response(text=json.dumps(response_obj), status=500)




app = web.Application()
cors = aiohttp_cors.setup(app)

rcreate=  cors.add(app.router.add_resource('/create/{collection}'))
rshow=  cors.add(app.router.add_resource('/show/{collection}'))

routecreate = cors.add(
    rcreate.add_route("POST", create), {
       "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
routeshow = cors.add(
    rshow.add_route("GET", show), {
       "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

web.run_app(app)
