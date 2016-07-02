import sqlite3
import urllib
from bs4 import BeautifulSoup
import time

#use this function to tell if a character is an english (ascii) character
#if it can encode, it's true/english, if not it returns false
def isEnglish(s):
    try:
        s.encode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

#connect the database
conn                = sqlite3.connect('psnp.sqlite')
cur                 = conn.cursor()
conn.text_factory   = str

#set up all our variables as empty
commit = 0
success,href,text,plat = 'n',"","",""
console,gold,silv,brnz = "","","",""
baseurl = "http://psnprofiles.com"

#Create the 'Games' table if it's not already there
cur.execute('''CREATE TABLE IF NOT EXISTS Games
    (game_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, url TEXT UNIQUE, name TEXT, console TEXT,
     platinum INTEGER, gold INTEGER, silver INTEGER, bronze INTEGER, completed INTEGER)''')

#gather all the partial links from the links table
cur.execute('SELECT url FROM Links')
links = cur.fetchall()

#This program can start and stop at any given page
#subselects are awesome
#if we take the max(name) insead of id, it orders a lowercase 'b' higher than a capital 'C'
#take the name of the game with the highest game_id listed
cur.execute('SELECT name FROM Games WHERE game_id = (SELECT max(game_id) FROM Games)')
games = cur.fetchone()

#test to determine where to start
#start by determining if it's english, if not we go straight to the end of the list
#if it is we take the first letter
if games is not None :
    games = games[0][0].upper()
    if games.isdigit() : games = '0-9'
    if isEnglish(games) :
        cur.execute('SELECT link_id FROM Links WHERE letter=?', ((games,)))
        linkid = cur.fetchone()
        i = linkid[0]
    else : #if the character is not english, we need the very last section of foreign game titles
        i = 29
        #newurl = baseurl + str(links[i-1][0])
else :
    i = 2 #the links we need start at 2
#print(str(i) + " " + newurl)

while i <= len(links) :
    #set the new url, increment the loop, gather and parse the soup
    #sleep(1) for courtesy on the website
    newurl = baseurl + str(links[i-1][0])
    i = i + 1

    print("~~~Press Ctrl + C to break~~~")
    print("Gathering game list from " + newurl)
    newurl = urllib.urlopen(newurl)
    soup = BeautifulSoup(newurl, "html.parser")
    time.sleep(1)

    for table in soup.find_all('table', id="game_list"):
        for tr in table.find_all('tr'):
            for td in tr.find_all('td'):
                for a in td.find_all('a', 'bold'):
                    #the url and name are hidden in the 'a' tag way down here
                    #have to skip several tags we don't want so we set success to 'y' when we find the correct one
                    href = a.get('href').encode('utf-8').strip()
                    text = a.get_text().encode('utf-8').strip()
                    success = 'y'

                for li in td.find_all('li'):
                    #the trophy count is listed in this 'li' tag
                    #if the game has no plat trophy, the tag was empty so we set it to 0
                    #cycle through the tags and gather the different trophy information
                    num = str(li.get_text().strip())
                    if num is "" : num = 0
                    rank = str(li.get('class')[0].strip())

                    if   rank == "platinum" : plat = str(num)
                    elif rank == "gold"     : gold = str(num)
                    elif rank == "silver"   : silv = str(num)
                    elif rank == "bronze"   : brnz = str(num)

                for img in td.find_all('img'):
                    #the console text can only be found in the 'img' tables attribute
                    #since a game might have several consoles attached, add them all to the 'console' variable
                    if img.has_attr('alt'):
                        imgalt = img.get('alt')
                        console = console + " " + imgalt

            if success == 'y' :
                #if we found the correct tables needed add what we found to the database
                print("adding to table... " + text + " " + href)
                cur.execute('''INSERT OR IGNORE INTO Games (url, console, name, platinum, gold, silver, bronze)
                VALUES (?, ?, ?, ?, ?, ?, ? )''', (href, console, text, plat, gold, silv, brnz)
                )
            time.sleep(.05)

            #commit every ten games listed and reset the variables that don't overwrite themselves
            commit = commit + 1
            if commit == 10 :
                conn.commit()
                commit = 0
            console,success = "",'n'

print("~~~Gathered informatin from all Games available~~~")
conn.commit()
cur.close()
