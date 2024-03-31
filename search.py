import csv
import json
import httpx
import os
import urllib
import time

from bs4 import BeautifulSoup
from collections import deque
from dotenv import load_dotenv

load_dotenv()

KEY = os.environ.get('GOOGLE_SEARCH_KEY')
CX = os.environ.get('GOOGLE_CX')

def retrieve_results(query):
    query = urllib.parse.quote_plus(query)
    url = f'https://www.googleapis.com/customsearch/v1?key={KEY}&cx={CX}&q={query}'
    resp = httpx.get(url)

    return resp.json()
    

if __name__ == "__main__":
    schools = []
    with open('world-universities.csv') as fh:
        csvFile = csv.reader(fh)
        for line in csvFile:
            if line[0] in ['GB', 'AZ', 'AU',]:
                schools.append(line)

    failed=[]
    for school in schools:
        print(school[1])
        if '.edu' not in school[2]:
            continue
        file_name = school[1].replace(' ', '_')
        school_url = school[2].replace('http://www.', '')
        school_url = school_url.split('/')[0]
        file_name += '.txt'
        query = f'{school[1]} official policy on generative AI Artificial Intelligence'
        results = retrieve_results(query)
        try:
            items = deque(results.get('items'))
        except TypeError:
            continue
        link = None
        while items and link is None:
            item = items.popleft()
            link = item.get('link')
            if school_url not in link:
                link = None
        if link is None:
            continue
        try:
            resp = httpx.get(link)
        except:
            failed.append(link)
            continue
        try:
            soup = BeautifulSoup(resp.content, 'html.parser')
        except AssertionError:
            failed.append(link)
            continue
        with open(file_name, 'w') as f:
            f.write(query + '\n')
            f.write(link + '\n')
            f.writelines(graf.get_text() + '\n' for graf in soup.find_all('p'))
        
        time.sleep(.7)

    fails = json.dumps(failed)
    with open('fails.json', 'w') as f:
        f.write(fails)
        

    