# This script is atrocious. I made it in a few minutes one night. Don't judge me. =D

from glob import glob
import pandas as pd
import sys
import os
from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

state_populations = pd.read_csv('state_populations.csv',usecols=['State','Pop'])


my_local_directory = '/Users/relyea/data/corona/'
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

most_recent_date = filename.split('/')[-1][0:10]

# the_states = most_recent_values.sort_values(by='tot').index.tolist()[-30:]
the_states = state_populations['State'].values

draw_curves = True

# thetype = 'tot'
# the_pct = 0.03

thetype = 'ded'
the_pct = 0.006
data_to_plot_list = []
for istate,the_state in enumerate(the_states):
# pick a state, any state
# the_state = 'Connecticut'
    short_group = short_usdata[short_usdata.state == the_state][['tot','ded','day']].groupby('day').sum()
    long_group = long_usdata[long_usdata.state == the_state][['tot','ded','day']].groupby('day').sum()
    usdata = pd.concat([short_group,long_group])
    usdata.loc[usdata[thetype] == 0,thetype] = 1

    # reg = LinearRegression().fit(np.arange(len(usdata)).reshape(-1,1),np.log2(usdata.tot.values))
    # do the last 5 days
    n_most_recent_days = 5
    
    reg = LinearRegression().fit(np.arange(n_most_recent_days).reshape(-1,1),np.log2(usdata[thetype].values[-n_most_recent_days:]))
    overall_population = state_populations[state_populations.State == the_state].Pop.values[0]
    per_capita_total_infected = usdata['ded'][-1]*100/overall_population
    doubling_period_in_days = 1.0/reg.coef_[0]
    doubling_period_until_3pct = log2(0.03/per_capita_total_infected)*doubling_period_in_days
    print(
        the_state.ljust(15) + 
        # ' confirmed: ' + 
        # '%07d' % (most_recent_values.loc[the_state,'tot']) +
        ' dead: ' + 
        ('%d' % (usdata['ded'][-1])).rjust(5) +
        # ' fakeratio: ' + 
        # '%0.4f' % (most_recent_values.loc[the_state,'ded']/most_recent_values.loc[the_state,'tot']) +
        ' percap: ' + 
        '%0.3f' % (per_capita_total_infected*100) + '%' + 
        ' period/time to 3%: ' + '%1.1f' % doubling_period_in_days +
        ' %02d' % doubling_period_until_3pct
    )
    if draw_curves:
        data_to_plot_list.append(usdata['ded'].diff())
        clf()
        for item in data_to_plot_list:
            semilogy(item, alpha = 0.1)
        semilogy(usdata['ded'].diff(), alpha=1.0)
        draw()
        show()
        aaaaa=input()
