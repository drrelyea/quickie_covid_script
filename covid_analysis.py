# This script is atrocious. I made it in a few minutes one night. Don't judge me. =D

from glob import glob
import pandas as pd
import sys
import os
from sklearn.linear_model import LinearRegression

my_local_directory = '/Users/relyea/data/bovoda/'
if not os.path.exists(my_local_directory):
    os.mkdir(my_local_directory)
os.chdir(my_local_directory)
if not os.path.exists('COVID-19'):
    os.system('git clone https://github.com/CSSEGISandData/COVID-19.git')

thefiles = sorted(glob(my_local_directory + '/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/*.csv'))

# they changed format a few days ago, because reasons
# in fairness, the new format is a lot nicer
shortfiles = thefiles[0:60]
longfiles = thefiles[60:]

# load data from the short-format files
short_data = []
for filename in shortfiles:
    the_date = filename.split('/')[-1][0:10]

    # start on March
    if the_date[:2] != '01' and the_date[:2] != '02':
        df = pd.read_csv(filename, index_col=None, header=0)
        df['thedate'] = filename.split('/')[-1][0:10]
        short_data.append(df)

short_frame = pd.concat(short_data, axis=0, ignore_index=True)
short_usdata = short_frame[short_frame['Country/Region'] == 'US']
short_usdata = short_usdata[['Confirmed', 'Deaths', 'Province/State', 'thedate']]
short_usdata.columns = ['tot','ded','state','day']
short_usdata.fillna('0.',inplace=True)
short_usdata['ded'] = short_usdata.ded.astype(float)

# load data from the long-format files
long_data = []
for filename in longfiles:
    df = pd.read_csv(filename, index_col=None, header=0)
 
    # start on March
    df['thedate'] = filename.split('/')[-1][0:10]
    long_data.append(df)

long_frame = pd.concat(long_data, axis=0, ignore_index=True)
long_usdata = long_frame[long_frame['Country_Region'] == 'US']
long_usdata = long_usdata[['Confirmed', 'Deaths', 'Province_State', 'thedate']]
long_usdata.columns = ['tot','ded','state','day']
long_usdata.groupby(['state','day']).sum()

# pick a state, any state
the_state = 'Ohio'
short_group = short_usdata[short_usdata.state == the_state][['tot','ded','day']].groupby('day').sum()
long_group = long_usdata[long_usdata.state == the_state][['tot','ded','day']].groupby('day').sum()
usdata = pd.concat([short_group,long_group])

reg = LinearRegression().fit(np.arange(len(usdata)).reshape(-1,1),np.log2(usdata.tot.values))
print('Doubling time in days for ' + the_state + ': ' + str(reg.coef_[0]))
# clf()
# semilogy(usdata.tot)
