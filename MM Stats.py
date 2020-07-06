import os
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

#get user input for year desired
year = input('What year do you want stats for?  \n**Note:** 2019 implies 2018-2019 season\nTournament in March of 2019\n')

#check if already have data
direct = os.getcwd()
stats = pd.read_csv(os.path.join(direct, 'Database', 'Stats.csv'))

yearDF = stats.loc[stats['Year'] == int(year)]

if len(yearDF) > 0:
    path = os.path.join(direct, 'Database', 'toView.csv')
    print('Saving desired data to', path)
    yearDF.to_csv(path, index=False)
else:
    print('Desired year not in database, need to get data.')
    
    #1) get teams in tourney
    url = 'https://en.wikipedia.org/wiki/' + str(year) + '_NCAA_Division_I_Men%27s_Basketball_Tournament'

    if year == '2019':
        tableStart = 4
    else:
        tableStart = 3

    #get html into parsable format
    dbPath = os.path.join(direct, 'Database', 'Teams.csv')
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')

    #get every table
    tables = soup.find_all('table')
    regionals = []
    for i in list(range(tableStart, tableStart + 4)):
        regionals.append(tables[i].find('tbody'))

    #get info into database
    schoolList = []
    for regional in regionals:
        rows = regional.find_all('tr')
        for row in rows[1:]:  #skip header row
            if year == '2019':
                school = row.find('th').text.strip()
                cols = row.find_all('td')
                seed = cols[-2].text.strip()
                bidType = cols[-1].text.strip()
            else:
                cols = row.find_all('td')
                #test if seed or school is first column of row (play-in-games)
                try:
                    possible = cols[0].text.replace('*', '')
                    seed = int(possible)
                    school = cols[1].text.strip()
                except ValueError:
                    school = cols[0].text.strip()
                seed = cols[-1].text.strip()
                bidType = cols[-2].text.strip()
            schoolList.append([school, seed, bidType, year])

    #put into dataframe
    teams = pd.DataFrame(schoolList, columns = ['School', 'Overall Seed', 'Bid', 'Year'])

    #load current database
    db = pd.read_csv(dbPath)
    merged = pd.concat((db, teams), axis=0).reset_index(drop=True)
    merged['drop'] = merged['School'] + merged['Year'].astype('str')
    merged.drop_duplicates(subset=['drop'], keep='last')
    merged.drop(columns=['drop'], inplace=True)
    #merged.to_csv(dbPath, index=False)  #uncomment later


    #2) get codes
    #every team in tournament
    tourneyTeams = list(teams['School'].unique())

    #every team we have codes for
    codePath = os.path.join(direct, 'Database', 'ESPN Codes.csv')
    codes = pd.read_csv(codePath)
    inCodes = list(codes['School'].unique())

    #teams we need codes for
    needCodes = [team for team in tourneyTeams if team not in inCodes]

    #get codes
    print('\n\n********\nUser must search for codes and manually enter.\nSearch for the team on ESPN website.\nCode is in URL.\n\n')
    toAdd = []
    for team in needCodes:
        code = input("What is ESPN's code for {}?:  ".format(team))
        toAdd.append([team, code])

    toAddDF = pd.DataFrame(toAdd, columns = ['School', 'Code'])

    newCodes = pd.concat((codes, toAddDF), axis=0)
    newCodes.reset_index(drop=True, inplace=True)

    #newCodes.to_csv(codePath, index=False)

    
    #3) get stats
    teamInfo = teams[['School']]
    teamCodes = teamInfo.merge(newCodes
                               ,how='left'
                               ,left_on='School'
                               ,right_on='School')

    #stats from ESPN into dataframe
    headers = ['School', 'Year', 'FGM', 'FGA', 'FTM', 'FTA', '3PM', '3PA'
              ,'PTS', 'OR', 'DR', 'REB', 'AST', 'TO', 'STL', 'BLCK']
    dataList = [headers]
    for index, row in teamCodes.iterrows():
        try:
            print(index, row['School'])
            code = str(int(row['Code']))
            url = 'http://www.espn.com/mens-college-basketball/team/stats/_/id/' + code + '/season/' + year
            r = requests.get(url)
            soup = bs(r.content, 'html.parser')

            playerStats = soup.find_all('tbody')[-1]
            totalRow = playerStats.find_all('tr')[-1] #last row
            cols = totalRow.find_all('td')[1:] #1st col is minutes played, skip

            #data to add to dataList (row of dataframe)
            data = [row['School'], str(year).strip()]
            for c in cols:
                data.append(c.text)
            dataList.append(data)
        except IndexError:
            print('No statistics available for ' + row['School'])

    #new stats to dataframe
    #add new statistics to dataframe
    stats = pd.DataFrame(dataList)
    header = stats.iloc[0] #1st row is header
    stats = stats[1:]
    stats.columns = header
    stats['FG%'] = stats['FGM'].astype('float') / stats['FGA'].astype('float')
    stats['FT%'] = stats['FTM'].astype('float') / stats['FTA'].astype('float')
    stats['3P%'] = stats['3PM'].astype('float') / stats['3PA'].astype('float')

    #old stats database
    statsDB = os.path.join(direct, 'Database', 'Stats.csv')
    oldStats = pd.read_csv(statsDB)

    allStats = pd.concat((oldStats, stats), axis=0)

    #remove duplicate rows
    allStats['drop'] = allStats['School'] + allStats['Year'].astype('str')
    final = allStats.drop_duplicates(subset=['drop'], keep='last')
    final.drop(columns=['drop'], inplace=True)
    final.reset_index(drop=True, inplace=True)

    #final.to_csv(statsDB, index=False)
    print(final)
