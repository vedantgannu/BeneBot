from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
from cloudant.query import Query
import json
from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def imageQuery(my_database, image_url):
    try:
        authenticator = IAMAuthenticator('fSzRWTNzcJX25EFgR1-OiqTzkw59Ft5_h1eh-zfnpjTD')
        visual_recognition = VisualRecognitionV3(version='2018-03-19',authenticator=authenticator)

        visual_recognition.set_service_url('https://gateway.watsonplatform.net/visual-recognition/api')
        url = image_url
        classes_result = visual_recognition.classify(url=url).get_result()
    except:
        print("Bad url!")
        return ({},"")
    
    image = classes_result
    #print(image)
    return ImageToItem(image,my_database)

def ImageToItem(image,my_database):
     classes = image['images'][0]['classifiers'][0]['classes']
     for str in classes:
         result = createQuery(my_database, str['class'])
         if(len(result.keys()) != 0):
            return (result, str['class'])
     return ({},"")

'''
def imageQuery(my_database, image_url):
    #authenticator = IAMAuthenticator('nxwDLUYQhqTpKEKno891x-O6QNnFdVVPal5HYGysEftm')
    visual_recognition = VisualRecognitionV3(version='2018-03-19',authenticator=authenticator)

    visual_recognition.set_service_url(image_url)
    parms = json.dumps( {'url': image_url, 'classifer_ids':['default']})
    print(parms)
    visual_recognition.classify(parameters = parms)


#create main client to have access to the cloud data-base

def imageQuery(my_database, image_url):

    image_url = ""
    parms = json.dumps( {'urls': image_url, 'classifier_ids': ['default']})
    results = visual_recgonition.classify( parameter = parms )
    print( json.dumps( results['images'][0]['classifiers'][0]['classes'], indent=2))
    '''

def createDatabase():
    client = Cloudant("863e5b40-95ef-474f-86dd-848b379f3fbe-bluemix","90ca5b2be3996997179a453cc936f7d7b4e5b456e03502a9317219c917ae5a46",url= "https://863e5b40-95ef-474f-86dd-848b379f3fbe-bluemix:90ca5b2be3996997179a453cc936f7d7b4e5b456e03502a9317219c917ae5a46@863e5b40-95ef-474f-86dd-848b379f3fbe-bluemix.cloudantnosqldb.appdomain.cloud")
    client.connect()
    database_name = "bene-db"
    my_database = client.create_database(database_name)
    return my_database
#Function to create query based on specific item inputted by the user

def createQuery(my_database,item):
    for str in item.split(' '):
        query = Query(my_database, selector = {'resources':{'$elemMatch': {'item':{'$regex': str}}}})
        result = query()
        if(len(result["docs"])>0):
            item = str
            return result
    return {}

def createCharityQuery(my_database, charity):
    charity = charity.lower()
    if(charity.find(' ') != -1):
        charity = charity.replace(' ', '_')
    query = Query(my_database, selector = {'filename':{'$regex':charity}})
    return query()

def parseCharity(query, charity):
    dict1 = dict()
    for doc in query['docs']:
        charity = doc['filename'].split('-')[0]
        disaster = doc['filename'].split('-')[1]
        if(charity not in dict1):
            dict1[charity] = {}
        for resource in doc['resources']:
            item = resource['item']
            quantityNeeded = resource['quota'] - resource['quantity']
            if (disaster not in dict1[charity]):
                dict1[charity][disaster] = []
            dict1[charity][disaster].append({'quantity-needed': quantityNeeded, 'item': item})
    return dict1



def parseData(query,item):
    dict1 = dict()
    for doc in query['docs']:
        charity = doc['filename'].split('-')[0]
        disaster = doc['filename'].split('-')[1]
        if(charity not in dict1):
            dict1[charity] = []
        for resource in doc['resources']:
            for str in item.split(' '):
                if str in resource['item']:
                    quantityNeeded = resource['quota'] - resource['quantity']
                    dict1[charity].append({'disaster': disaster, 'quantity-needed': quantityNeeded})
    return dict1


#MAIN
#my_database = createDatabase()
#imageQuery(my_database, 'https://watson-developer-cloud.github.io/doc-tutorial-downloads/visual-recognition/fruitbowl.jpg')
#db = createDatabase()
#query = createCharityQuery(db, "Red Cross")
#print(parseCharity(query,"red_cross"))


