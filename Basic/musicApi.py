import os
import regex # Using regex package instead of re
from pymongo import MongoClient
from dotenv import load_dotenv

from melon import ChartData as MelonChartData
from bugs import ChartData as BugsChartData
from genie import ChartData as GenieChartData


def MusicAPi(site):
    
    if site =="Melon":
        chart = MelonChartData()
    elif site =="Bugs":
        chart = BugsChartData()
    else:
        chart = GenieChartData()
    
    documents = []

    # MongoDB Connection
    load_dotenv()
    mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')
    mongoClient = MongoClient(mongo_connection_string)

    # Clear the MongoDB collection
    mongoCollection = mongoClient['Music'][site] 
    mongoCollection.delete_many({})

    pattern = regex.compile(r"[^\p{Hangul}\p{Latin}\p{Nd}\s'\u2019&]+", regex.UNICODE)

    for i in range(0,100,1):
        title_text = chart[i].title
        title_filtered = regex.sub(pattern, '', title_text)
        title_filtered = title_filtered.upper().replace('PROD BY', 'PROD').strip()
        
        documents.append({
        site + '_rank': chart[i].rank,
        'title': title_filtered,
        'singer': chart[i].artist,
        })
        
    mongoCollection.insert_many(documents)