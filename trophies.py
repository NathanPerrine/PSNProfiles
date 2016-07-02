import sqlite3
import urllib
from bs4 import BeautifulSoup
import time
import re

#connect to the database
conn                = sqlite3.connect('psnp.sqlite')
cur                 = conn.cursor()
conn.text_factory   = str

#create our table if this is the first time running
cur.execute('''CREATE TABLE IF NOT EXISTS Trophies
    (tro_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, game_id TEXT,
    url TEXT UNIQUE, title TEXT, content TEXT, rank TEXT)''')

#set up variables used
success,commit = "n",0
title,content,rank,href = "","","",""
baseurl = "http://psnprofiles.com"

#use maxid to tell the loop when to end
cur.execute('SELECT max(game_id) FROM Games')
maxid = cur.fetchone()[0]

while True :

    #Find where to start, will take the first game if we haven't started yet
    #if we have it'll take the last game where we haven't submitted anything to the "Complete" table
    cur.execute('SELECT min(game_id) FROM Games WHERE Completed IS NULL')
    gameid = cur.fetchone()[0]
    #print(gameid)

    #Gather and create the URL for the page we're going to gather info from
    cur.execute('SELECT url FROM Games WHERE game_id =?',((gameid,)))
    url = cur.fetchone()[0]
    newurl = baseurl + str(url)
    #print(newurl)

    #Sleep so we're not overloading the website
    print('Gathering trophy information from... ' + newurl)
    time.sleep(.5)
    #break

    #open and parse the new url
    newurl = urllib.urlopen(newurl)
    soup = BeautifulSoup(newurl, 'html.parser')

    skip = 0

    #start pouring through the soup, the 'completed' info we need is hidden in the div/span tags
    for div in soup.find_all('div', 'stats'):
        for span in div.find_all('span') :
            #due to the html the 'span' tags are doubled, so we skip every other one.
            if skip == 1 :
                skip = 0
                continue

            #gather the 'span' text, split it, and assign it to y,z
            #if 'z' is the text we need we assign the completed variable
            x = str(span.get_text("|"))
            y,z = x.split("|")
            if z == "100% Completed":
                completed = int(y.replace(',',''))
                #print(completed)
            skip = 1

    #Back through the soup, the trophy info is hidden in the zebra table
    for table in soup.find_all('table', class_=("zebra")):
        for tr in table.find_all('tr', ""):
            for td in tr.find_all('td'):
                for a in td.find_all('a', 'bold'):
                    #strips the text from the "a" and "td" tag, which is the title and content. conveient!
                    #encode the text to a printable format and split it into a list
                    x = (td.get_text("|", strip=True))
                    x = x.encode('utf-8')
                    x = x.split("|")

                    #the 'title' is always the first item in the list
                    title = str(x[0])

                    #a few were set up with line breakes, so we assign all the remaining lines into the 'content' tag
                    for i in range(len(x)) :
                        if i + 1 == len(x) : break
                        content = content + str(x[i+1]) + " "
                    content = content.strip()

                    #the href tag is simple to gather, encode, encode, and strip
                    href = a.get('href').encode('utf-8').strip()

                #the only way to find the rank was to find the text for the trophy image on the page
                for img in td.find_all('img'): #find all images
                    if img.has_attr('title'):  #image we're looking for has the title attribute
                        rank = img.get('title')#if we find the right image assign it

            #add it to the database list, use the game_id to associate games to trophies
            print("adding to table game_id " + str(gameid) + ", title, " + title + ", text, " + content + " rank, " + str(rank))
            cur.execute('''INSERT OR IGNORE INTO Trophies (game_id, url, title, content, rank)
            VALUES (?, ?, ?, ?, ?)''', (gameid, href, title, content, rank))

            #reset the 'content' tag so it doesn't get bigger and bigger
            #sleep again so we don't overload the website like a freeloader
            content = ""
            time.sleep(.05)

        break #escape this for loop, only need the first table.

    #add the 'completed' tag to the Game table and commit the database
    print("adding to Game row " + str(gameid) + " completed " + str(completed))
    cur.execute ("UPDATE Games SET completed=? WHERE game_id=?", (completed,gameid) )
    conn.commit()
    #break

    #continue until we reach the max game_id, then break the loop
    if gameid == maxid: break

conn.commit()
cur.close()
