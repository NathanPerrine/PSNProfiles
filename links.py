import sqlite3
import urllib
from bs4 import BeautifulSoup
import time

#set the webpage to gather information
url = urllib.urlopen('http://psnprofiles.com/games').read()
#fh = open("htmlsource.html")
soup = BeautifulSoup(url, "html.parser")

#connect to the database
conn                = sqlite3.connect('psnp.sqlite')
cur                 = conn.cursor()
conn.text_factory   = str

commit  = 0

#create our table if it's not already there
#cur.execute('''DROP TABLE IF EXISTS Links''')
cur.execute('''CREATE TABLE IF NOT EXISTS Links
    (link_id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, letter TEXT)''')

#gather the last link we submitted
#use this to test if we need to gather anything
cur.execute('SELECT max(link_id) FROM Links')
row = cur.fetchone()

#it's easy to tell how many we need, as we only need to gather 29 links
#alternatively test the text if it's the last we expect to gather
if row[0] < 29 or row[0] == None :
    for node in soup.select("a.button.small"):
        href = node.get('href').strip()
        text = node.get_text().strip()

        #test where we left off, try to gather text from the database
        cur.execute('SELECT letter FROM Links WHERE letter=?', ((text,)))
        row = cur.fetchone()

        #if row != None that means we already have that link gathered, so continue
        if row != None: continue

        #add everything to the database we gathered
        print("Insert into links, " + href + " " + text + '\n')
        cur.execute('''INSERT OR IGNORE INTO links (url, letter)
            VALUES (?, ?)''', (href, text))

        #don't need to commit every time we gather
        commit = commit + 1
        if commit == 10 :
            conn.commit()
            commit = 0

conn.commit()
