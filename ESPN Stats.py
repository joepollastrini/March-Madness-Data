import os
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

year = input('What year would you like to get stats for?  ')

direct = os.getcwd()

#get all teams and codes
teamData = pd.read_csv(os.path.join(direct, 'Database', 'Teams.csv'))
codeData = pd.read_csv(os.path.join(direct, 'Database', 'ESPN Codes.csv'))

#only teams for desired year
teamYear = teamData.loc[teamData['Year'] == int(year)]
teamInfo = teamYear[['School']]

#codes for each team
teamCodes = teamInfo.merge(codeData
                           ,how='left'
                           ,left_on='School'
                           ,right_on='School')

#get statistics from ESPN into a dataframe
#data frame set up (headers)
dataList = [['School', 'Year', 'FGM', 'FGA', 'FTM', 'FTA', '3PM', '3PA'
             , 'PTS', 'OR', 'DR', 'REB', 'AST', 'TO', 'STL', 'BLCK']]
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


#add new statistics to dataframe
stats = pd.DataFrame(dataList)
header = stats.iloc[0] #1st row is header
stats = stats[1:]
stats.columns = header
stats['FG%'] = stats['FGM'].astype('float') / stats['FGA'].astype('float')
stats['FT%'] = stats['FTM'].astype('float') / stats['FTA'].astype('float')
stats['3P%'] = stats['3PM'].astype('float') / stats['3PA'].astype('float')


#get current database of statistics to append to
oldStats = pd.read_csv(os.path.join(direct, 'Database', 'Stats.csv'))


#put old and new together
allStats = pd.concat((oldStats, stats), axis=0)


#remove duplicate rows if applicable
allStats['drop'] = allStats['School'] + allStats['Year'].astype('str')
final = allStats.drop_duplicates(subset=['drop'], keep='last')
final.drop(columns=['drop'], inplace=True)
final.reset_index(drop=True, inplace=True)


#write to database
final.to_csv(os.path.join(direct, 'Database', 'Stats.csv'), index=False)
