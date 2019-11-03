#Charity Bot
#import necessary libraries
import io
import random
import string # to process standard python strings
import warnings
import numpy as np
import admin as db
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import warnings
warnings.filterwarnings('ignore')

import nltk
from nltk.stem import WordNetLemmatizer
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

#nltk.download('popular', quiet=True) # for downloading packages

# uncomment the following only the first time
#nltk.download('punkt') # first-time use only
#nltk.download('wordnet') # first-time use only

#Reading in the corpus
with open('chatbot.txt','r', encoding='utf8', errors ='ignore') as fin:
    raw = fin.read().lower()

#TOkenisation
sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences
word_tokens = nltk.word_tokenize(raw)# converts to list of words

# Preprocessing
lemmer = WordNetLemmatizer()
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


# Keyword Matching
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]


def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


# Generating response
def response(user_response):
    
    robo_response=''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response



#THE MAIN STUFF: Conversation with the bot......

flag=True
dataBase = db.createDatabase()
print("Hi, welcome to bene bot")
while(flag==True):
    print()
    print("1) would you like to inquire about a Charity\n 2) would you like to donate an item?")
    user_response1 = input()
    if( user_response1 == '1'):
            print("Enter a charity")
            user_response1 = input()
            query = db.createCharityQuery(dataBase, user_response1)
            dict1 = db.parseCharity(query, user_response1)
            if(len(dict1.keys()) == 0):
                print("That charity does not exist")
            else:
                print()
                print(user_response1)
                user_response1 = user_response1.lower()
                if(user_response1.find(' ') != -1):
                    user_response1 = user_response1.replace(' ', '_')
                for disaster in dict1[user_response1]:
                    print("\t",disaster)
                    for i in dict1[user_response1][disaster]:
                        print("\t\twe need", i['quantity-needed'],"units of", i['item'])
    else:
        print("1) would you like to enter a image\n 2) would you like to enter the item name?")
        user_response1 = input()
        if(user_response1 ==  '1'):
            print("Enter url")
            user_response1 = input()
            item =""
            image = db.imageQuery(dataBase, user_response1)
            if(len(image[0].keys()) == 0):
                print("This image is not valid!")
                dict1 = {}
            else:
                query = image[0]
                user_response1 = image[1]
                dict1 = db.parseData(query, user_response1)
        else:
            print("Enter item name")
            user_response1 = input()
            query = db.createQuery(dataBase,user_response1)
            dict1 = db.parseData(query, user_response1)
        if(len(dict1.keys()) == 0):
            print("No charities need this item")
        else:
            print()
            for charity in dict1:
                print(charity)
                for i in dict1[charity]:
                    print("\twe need", i['quantity-needed'], user_response1, "for the", i['disaster'], "disaster")

    user_response1=user_response1.lower()
    if(user_response1!='bye'):
        if(user_response1=='thanks' or user_response1=='thank you' ):
            flag=False
            print("ROBO: You are welcome..")
    else:
        flag=False
        print("ROBO: Bye! take care..")

