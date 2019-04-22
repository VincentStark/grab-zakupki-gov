#!/usr/bin/env python

import time
import random
import sys
from urllib import FancyURLopener
from jinja2 import Environment, PackageLoader
from bs4 import BeautifulSoup

# Fancy User-Agent string
class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4'
myopener = MyOpener()

# Prepare template
env = Environment(loader=PackageLoader('__main__', 'templates'))
template = env.get_template('zakupki.tmpl')

# Prepare array for data storage
entries = []

# Process all pages
for pagenum in range(1, 100):
    
    # Get page handler
    print 'Fetching page ' + str(pagenum) + '...',
    sys.stdout.flush()
    f = myopener.open('http://zakupki.gov.ru/pgz/public/action/search/region/result?rfSubjects=5277335&index='
        + str(pagenum)
        + '&sortField=lastEventDate&descending=true&tabName=AP&lotView=false&pageX=&pageY=');
    print 'Done!'

    # Parse page contents
    doc = BeautifulSoup(f)

    # Get content
    table = doc.find('table', 'searchResultTable iceDatTbl')

    for row in table.find_all('tr', 'searchResultTableRow'):
      
      entry = {}

      # Extract description type
      type =  row.find('span', 'blueBold')
      entry['description_type'] = type.string.strip()

      # Extract description number and link
      entry['description_number_href'] = type.parent.a.get('href')
      entry['description_number'] = type.parent.a.span.string.strip()

      # Extract description text and link
      entry['description_text_href'] = type.parent.parent.parent.select('.iceOutLnk')[0].get('href')
      entry['description_text'] = type.parent.parent.parent.select('.iceOutLnk')[0].string.strip()

      # Extract description org text and link
      entry['description_org_href'] = type.parent.parent.parent.select('.iceCmdLnk')[1].get('href')
      entry['description_org'] = type.parent.parent.parent.select('.iceCmdLnk')[1].span.string.strip()
      
      # Extract published and updated
      dates = row.find_all('td', 'iceDatTblCol searchResultTableCol searchResultColumn tableColumn70')
      entry['published'] = dates[0].span.string.strip()
      entry['updated_href'] = dates[1].a.get('href')
      entry['updated'] = dates[1].a.span.string.strip()
        
      # Extract price
      entry['price'] = row.find('td', 'iceDatTblCol searchResultTableCol searchResultColumn tableColumn105').span.string.strip()

      # Extract additional info
      entry['additional'] = u''
      for link in row.find('table', 'tableColumn70').find_all('a'):
        entry['additional'] += '<a href="http://zakupki.gov.ru' + link.get('href') + '" target="_blank">' + link.span.string + '</a><br/>' 

      # Add new entry
      entries.append(entry)

    # Random pause to confuse checking tools
    pause = random.randint(1, 2)
    print 'Sleeping for ' + str(pause) + ' seconds...',
    sys.stdout.flush()
    time.sleep(pause)
    print 'OK'

# Output
report = open('zakupki.html', 'w')
report.write(template.render(entries = entries).encode('utf-8'))
report.close()
