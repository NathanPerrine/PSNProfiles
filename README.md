Gathering Playstation Trophy information from the website PSNProfiles.com

Simple how to: 
1) Have Python 3.5 and a database program such as "DB Browser for SQLite" installed
2) Run the 'links.py' script first to gather all the links used to gather game information
3) Run the 'games.py' script second to gather all the game information 
4) Run the 'trophies.py' script third to gather all the trophy information

Links.py : 
  Simple program that gathers the links from the website and stores it into the 'links' table for the database. The links gathered are the 'blue buttons' that sort the games alphabetically. Once you're on that page it lists all the games starting with that letter (or number, or foreign character) so we don't need to go further than that. 
  Info gathered: urls to the various pages and the letter associated with it
  
Games.py : 
  Takes the links gathered earlier and uses them to start gathering all the games listed on the website. It starts at the second link gathered as 'all' simply lists the same games again, so we skip it. Starting ath 0-9 this script goes through every link gathered and finds all game information listed on that page, then it moves onto the next. This script can start and stop at any given page by determining the last game that was entered into the database.
  Info gathered: urls to the individual games listed along with name, console, and trophy count information
  
Trophies.py : 
  Very similar to the 'games.py' script, this will cycle through all the games listed in the database and take the URL to go to that games individual webpage to gather all trophy information associated with it. Once all trophies for the game have been added to the database we complete the last column in the 'games' table, which we use to determine where we left off and where to start again. Using the 'game_id' column we associate each trophy with the game it comes from. 
  Info gathered: Individual trophy names, descriptions, ranks, and times completed. 
  
For more detailed information on how each works, see the comments in the individual scripts. 
  
For a completed database (information gathered 6/23/16) download the "Zipped completed database" file. 
  
To see the results and related discussion, view the reddit thread np.reddit.com/r/PS4/comments/4q3jl2/i_recently_finished_a_class_on_gathering_and/
