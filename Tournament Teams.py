import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import os

year = input('What year would you like to get teams for?  ')
url = 'https://en.wikipedia.org/wiki/' + str(year) + '_NCAA_Division_I_Men%27s_Basketball_Tournament'
if year=='2019':
    tableStart = 4
else:
    tableStart = 3
databaseName = 'Teams.csv'
direct = os.getcwd()
databasePath = os.path.join(direct, 'Database', databaseName)

#get html into parsable format
r = requests.get(url)
soup = bs(r.content, 'html.parser')

#get all tables
tables = soup.find_all('table')
regionals = []
#get relevant tables
for i in list(range(tableStart, tableStart + 4)):
    #get body of tables
    regionals.append(tables[i].find('tbody'))

#get information into list of lists
schoolList = []
#iterate through each table body
for regional in regionals:
    #get rows of table
    rows = regional.find_all('tr')
    for row in rows[1:]: #skip header row
        if year == '2019':
            school = row.find('th').text.strip()
            #parse from end of row due to play in games
            seed = cols[-2].text.strip()
            bidType = cols[-1].text.strip()
        else:
            cols = row.find_all('td')
            #test if seed or school is first column of row (play-in games)
            try:
                possible = cols[0].text.replace('*', '')
                seed = int(possible)
                school = cols[1].text.strip()
            except ValueError:
                school = cols[0].text.strip()
            #parse from end of row due to play in games
            seed = cols[-1].text.strip()
            bidType = cols[-2].text.strip()
        #append all info to list of lists
        schoolList.append([school, seed, bidType, year])

#put scraped data into dataframe
teams = pd.DataFrame(schoolList, columns=['School', 'Overall Seed', 'Bid', 'Year'])

#database management
#load current teams data
db = pd.read_csv(databasePath)
#append scraped data to database
merged = pd.concat((db, teams), axis=0).reset_index(drop=True)
#remove duplicates (in case data already in dataframe)
#don't know why, but need to write it first?
merged.to_csv(databasePath, index=False)
db = pd.read_csv(databasePath)
db.drop_duplicates(inplace=True)
#overwrite database
db.to_csv(databasePath, index=False)
