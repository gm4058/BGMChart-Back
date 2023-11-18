import re
import textdistance
import os
import subprocess

from pymongo import MongoClient
from operator import itemgetter
from dotenv import load_dotenv

# Normalization and comparison functions
def normalize_title(title):
    title = title.lower()
    title = re.sub('\s+', '', title)
    title = re.sub('[^a-z가-힣0-9]+', '', title)
    return title

def normalize_singer(singer):
    singer = re.sub('\([^)]*\)', '', singer)
    singer = singer.lower()
    singer = re.sub('\s+', '', singer)
    singer = re.sub('[^a-z가-힣0-9]+', '', singer)
    return singer

def jaro_winkler(str1, str2):
    return textdistance.jaro_winkler(str1, str2)

# MongoDB Connection
load_dotenv()
mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')
mongoClient = MongoClient(mongo_connection_string)

testCol = mongoClient['Music']['Merge']
testCol.delete_many({})

pipeline = [
    {'$project': {'title': 1, 'singer': 1, 'Melon_rank': 1, 'source': {'$literal': 'melon'}}},
    {'$unionWith': {'coll': 'Bugs', 'pipeline': [{'$project': {'title': 1, 'singer': 1, 'Bugs_rank': 1, 'source': {'$literal': 'bugs'}}}]}},
    {'$unionWith': {'coll': 'Genie', 'pipeline': [{'$project': {'title': 1, 'singer': 1, 'Genie_rank': 1, 'source': {'$literal': 'genie'}}}]}},
    {'$sort': {'Melon_rank': 1, 'Bugs_rank': 1, 'Genie_rank': 1}},
    {'$out': 'Merge'}
]

mongoClient['Music']['Melon'].aggregate(pipeline, allowDiskUse=True)

merged_data = list(testCol.find())

for item in merged_data:
    item['normalizedTitle'] = normalize_title(item['title'])
    item['normalizedSinger'] = normalize_singer(item['singer'])

threshold = 0.1
grouped_data = []

for value in merged_data:
    is_grouped = False

    for group in grouped_data:
        if (value['normalizedSinger'] == group['normalizedSinger'] and
            jaro_winkler(value['normalizedTitle'], group['normalizedTitle']) >= threshold and
            value['normalizedTitle'][2:5] == group['normalizedTitle'][2:5]):

            group['values'].append(value)
            is_grouped = True
            break

    if not is_grouped:
        grouped_data.append({
            'values': [value],
            'normalizedTitle': value['normalizedTitle'],
            'normalizedSinger': value['normalizedSinger']
        })

for group in grouped_data:
    melon_rank = next((value.get('Melon_rank', 0) for value in group['values'] if value['source'] == 'melon'), 0)
    bugs_rank = next((value.get('Bugs_rank', 0) for value in group['values'] if value['source'] == 'bugs'), 0)
    genie_rank = next((value.get('Genie_rank', 0) for value in group['values'] if value['source'] == 'genie'), 0)

    group['MelonRank'] = melon_rank
    group['BugsRank'] = bugs_rank
    group['GenieRank'] = genie_rank


final_data = []

for group in grouped_data:
    final_data.append({
        'title': group['values'][0]['title'],
        'singer': group['values'][0]['singer'],          
        'Melon_rank': group['MelonRank'],
        'Bugs_rank': group['BugsRank'],
        'Genie_rank': group['GenieRank']
    })

testCol.delete_many({})
testCol.insert_many(final_data[:100])

#subprocess.Popen(['python3', '/home/ubuntu/BGM_Back/Basic/Img.py'])
    

