import os
import pandas as pd

db = os.path.join(os.getcwd(), 'Database')

#get every school in tournament database
tourneyDB = pd.read_csv(os.path.join(db, 'Teams.csv'))
teams = list(tourneyDB['School'].unique())

#get every school that we know a code for
codes = pd.read_csv(os.path.join(db, 'ESPN Codes.csv'))
inCodes = list(codes['School'].unique())

#get every school we don't know codes for
needCodes = [team for team in teams if team not in inCodes]

#get codes
#search for code in url of ESPN website
toAdd = []
for team in needCodes:
    code = input("What is ESPN's code for {}?:  ".format(team))
    toAdd.append([team, code])

#put into dataframe
toAddDF = pd.DataFrame(toAdd, columns=['School', 'Code'])

#add to old code database
newCodes = pd.concat((codes, toAddDF), axis=0)
newCodes.reset_index(drop=True, inplace=True)

#replace old file
newCodes.to_csv(os.path.join(db, 'ESPN Codes.csv'), index=False)
