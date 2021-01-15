#!/usr/bin/env python
# coding: utf-8

# In[13]:


import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import numpy as np
from matplotlib import pyplot as plt

import io
import base64
def list_to_hist(lst):
    plt.cla()
    fig, ax = plt.subplots()
    data = []
    img = io.BytesIO()
    for i in range(len(lst)):
        for j in range(int(lst[i]*1000)):
            data.append(i+1)
    ax.hist(data, bins=np.arange(0, len(lst) + 1) + 0.5, density=True, color="#364e8f")
    ticklabels = [str(i) for i in range(1, 18)]
    ticklabels[-1] = 'Miss'
    plt.xticks(range(1, 18), ticklabels, size='small')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
    return base64.b64encode(img.getvalue()).decode()


# In[7]:


def average_data(mega_df):
    input_dict = {'pyt':[],'aOE':[],'aDE':[],'temp':[]}
    for i in range(len(mega_df)):
        if mega_df.loc[i,'Year'] != mega_df.loc[i,'Year'] or mega_df.loc[i,'AdjTempo'] != mega_df.loc[i,'AdjTempo']:
            input_dict['pyt'].append(mega_df.loc[i,'barthag'])
            input_dict['aOE'].append(mega_df.loc[i,'adjoe'])
            input_dict['aDE'].append(mega_df.loc[i,'adjde'])
            input_dict['temp'].append(mega_df.loc[i,'tempo'])
        elif mega_df.loc[i,'Year'] < 2010:
            input_dict['pyt'].append(mega_df.loc[i,'Pythag'])
            input_dict['aOE'].append(mega_df.loc[i,'AdjOE'])
            input_dict['aDE'].append(mega_df.loc[i,'AdjDE'])
            input_dict['temp'].append(mega_df.loc[i,'AdjTempo'])
        else:
            input_dict['pyt'].append((mega_df.loc[i,'barthag'] + mega_df.loc[i,'Pythag'])/2)
            input_dict['aOE'].append((mega_df.loc[i,'adjoe'] + mega_df.loc[i,'AdjOE'])/2)
            input_dict['aDE'].append((mega_df.loc[i,'adjde'] + mega_df.loc[i,'AdjDE'])/2)
            input_dict['temp'].append((mega_df.loc[i,'tempo'] + mega_df.loc[i,'AdjTempo'])/2)
    mega_df['mean_pythag'] = input_dict['pyt']
    mega_df['mean_adjOE'] = input_dict['aOE']
    mega_df['mean_adjDE'] = input_dict['aDE']
    mega_df['mean_tempo'] = input_dict['temp']
    return mega_df


# In[8]:


def combine_seeds(st_df, mega_df):
    for i in range(len(st_df)):
        if st_df.loc[i,'in_df'] == 1:
            found = False
            j = 0
            while not found:
                if mega_df.loc[j,'Label'] == st_df.loc[i,'Label']:
                    mega_df.loc[j,'S'] = st_df.loc[i,'Seed']
                    found = True
                else:
                    j += 1
        else:
            found = False
            j = 0
            new_labels = [x + str(st_df.loc[i,"Season"]) for x in st_df.loc[i,'spellings']]
            while not found and j < len(mega_df):
                if mega_df.loc[j,'Label_Lower'] in new_labels:
                    mega_df.loc[j,'S'] = st_df.loc[i,'Seed']
                    found = True
                else:
                    j += 1
    return mega_df


# In[10]:


def generate_historical_df():
    #Read in historical KenPom Data
    df_hist = pd.read_excel('data/KenPom Tourney Characteristics.xlsx', sheet_name='Master')
    #Label teams based on year and school
    df_hist['Label'] = df_hist[['TeamName', 'Year']].astype('str').apply(lambda x: ''.join(x), axis=1)
    #Batch read in more recent Torvik files
    frames = []
    for yr in range(2010,2020):
        df = pd.read_json("data/" + str(yr) + "_team_results.json")
        df = df.rename(columns={1:'team',4:'adjoe',6:'adjde',8:'barthag',44:'tempo'})
        #print(df.columns)
        df['yr'] = str(yr)
        df['Label'] = df['team'] + str(yr)
        frames.append(df)
    #Concatenate new Torvik files & merge
    mega_bt_df = pd.concat(frames,ignore_index=True)
    mega_df = pd.merge(mega_bt_df,df_hist,how='outer',on='Label')
    mega_df = average_data(mega_df)
    mega_df.dropna(inplace=True, subset=['mean_pythag'])
    mega_df['Label_Lower'] = mega_df['Label'].apply(lambda x:str(x).lower())
    mega_df = mega_df.reset_index(drop=True)
    seeds = pd.read_csv("data/MNCAATourneySeeds.csv")
    seeds['Seed'] = seeds['Seed'].astype('str').apply(lambda x: int(x[1:].strip('a').strip('b')))
    teams = pd.read_csv("data/MTeams.csv")
    spellings = pd.read_csv("data/MTeamSpellings.csv", encoding='cp1252')
    seeds = seeds.loc[seeds.Season > 2014]
    st_df = pd.merge(seeds,teams, on='TeamID', how = 'left')
    st_df['Label'] = st_df['TeamName'] + st_df['Season'].astype('str')
    alt_names = []
    in_megadf = []
    for i in range(len(st_df)):
        l = st_df.loc[i,'Label']
        if l in mega_df['Label'].tolist():
            alt_names.append([])
            in_megadf.append(1)
        else:
            alt = spellings.loc[spellings.TeamID == st_df.loc[i,'TeamID']]
            alt_names.append(alt.TeamNameSpelling.tolist())
            in_megadf.append(0)
    st_df['in_df'] = in_megadf
    st_df['spellings'] = alt_names
    mega_df = combine_seeds(st_df,mega_df)
    mega_df['S'] = mega_df['S'].fillna(17)
    return mega_df


# In[14]:


def scale_and_fit(mega_df):
    scaler = StandardScaler()
    h = mega_df.loc[mega_df.Label_Lower != 'louisville2016']
    h = mega_df[['mean_pythag','mean_adjOE','mean_adjDE','mean_tempo']]
    scaler.fit(h)
    h = scaler.transform(h)
    neigh = NearestNeighbors(n_neighbors = 100)
    neigh.fit(h)
    return scaler, neigh, h


# In[20]:


def get_and_scale(scaler, is_2020=False):
    if is_2020 == True:
        df_curr = pd.read_json("https://barttorvik.com/2020_team_results.json")
    else:
        df_curr = pd.read_json("https://barttorvik.com/2021_team_results.json")
    df_curr = df_curr.rename(columns={1:'team',4:'adjoe',6:'adjde',8:'barthag',44:'tempo'})
    c = df_curr[['barthag','adjoe','adjde','tempo']]
    c = (scaler.transform(c))
    return df_curr, c


# In[16]:


#TODO: export this data and train/test out probabilities using 2015-19 data
def predict(i, num_matches = 5, distance_weight = 1, num_comps = 55):
    info_dict = {}
    info_dict['team'] = (df_curr.loc[i,'team'])
    a = (neigh.kneighbors([c[i]]))
    distances = a[0][0].tolist()
    distances = distances[:num_comps]
    inv_dist = [(1/d**distance_weight) for d in distances]
    matches = a[1][0].tolist()
    matches = matches[:num_comps]
    short = matches[:num_matches]
    info_dict['matches'] = (mega_df.loc[short,'Label'].tolist())
    #"""
    seeds = (mega_df.loc[matches,'S'].tolist())
    sumprod = sum(float(x) * float(y) for x, y in zip(seeds, inv_dist))
    seed_distribution = [i*0 for i in range(17)]
    for i in range(len(matches)):
        seed_distribution[int(seeds[i]-1)] += inv_dist[i]/sum(inv_dist)
    '''s16_prob = 0
    f4_prob = 0
    for i in range(len(matches)):
        if mega_df.loc[matches[i],'S16'] == 'x':
            s16_prob += inv_dist[i]
            if df_hist.loc[matches[i],'F4'] == 'x':
                f4_prob += inv_dist[i]
    s16_prob = s16_prob/sum(inv_dist)
    f4_prob = f4_prob/sum(inv_dist)
    '''
    info_dict['avg_seed'] = (sumprod/sum(inv_dist))
    info_dict['seed_dist'] = (seed_distribution)
    return info_dict


# In[17]:


def process_seed_dist(lst):
    p_make = sum(lst[:-1])
    most_likely = 0
    #max tracker below don't return
    max_p = 0
    for i in range(len(lst) - 1):
        if lst[i] > max_p:
            max_p = lst[i]
            most_likely = i + 1
    avg_make_seed = 0
    for i in range(len(lst) - 1):
        avg_make_seed += (i+1) * lst[i]
    try:
        avg_make_seed = avg_make_seed/sum(lst[:-1])
    except ZeroDivisionError:
        avg_make_seed = "None"
    return p_make, most_likely, avg_make_seed


# In[23]:





# In[24]:


mega_df = generate_historical_df()


# In[25]:


scaler, neigh, h = scale_and_fit(mega_df)


# In[26]:


df_curr, c = get_and_scale(scaler)


# In[70]:


df_curr_2020, c_2020 = get_and_scale(scaler, is_2020=True)



def generate_main_dict(dataframe=df_curr):
    output_dict = {'Team':[],
        'Conf.':[],
        'Record':[],
        '#1 Match':[],
        '#2 Match':[],
        '#3 Match':[],
        'Avg. Seed':[],
        'Most Likely Seed':[],
        'Made Tourney':[]
                  }

    for i in range(len(df_curr)):
        output_dict['Team'].append(df_curr.loc[i,'team'])
        output_dict['Conf.'].append(df_curr.iloc[i,2])
        output_dict['Record'].append(df_curr.iloc[i,3])
        x = predict(i)
        m, y, a = process_seed_dist(x['seed_dist'])
        output_dict['#1 Match'].append(x['matches'][0])
        output_dict['#2 Match'].append(x['matches'][1])
        output_dict['#3 Match'].append(x['matches'][2])
        if a != "None":
            output_dict['Avg. Seed'].append(round(a, 2))
        else:
            output_dict['Avg. Seed'].append(a)
        output_dict['Most Likely Seed'].append(y)
        output_dict['Made Tourney'].append(m)
    return pd.DataFrame.from_dict(output_dict)


# In[27]:


write = generate_main_dict()


write_2020 = generate_main_dict(df_curr_2020)


# In[49]:


write = write.reset_index(drop=True)
write.to_csv("res.csv")


# In[74]:


def historical_page(team, df_curr):
    i = -1
    is_historical = team[-4:].isnumeric()
    if is_historical:
        mdf_labindex = mega_df.reset_index().set_index('Label')
        i = mdf_labindex.loc[team,'index']
        a = (neigh.kneighbors([h[i]]))
    else:
        dfc_labindex = df_curr.reset_index().set_index('team')
        i = dfc_labindex.loc[team,'index']
        a = (neigh.kneighbors([c[i]]))
    matches = a[1][0].tolist()
    distances = [round(x, 3) for x in a[0][0].tolist()]
    comp_df = mega_df.loc[matches[1:],:].copy()
    comp_df['distance'] = distances[1:]
    ret = comp_df[['Label', 'S', 'distance']].copy()
    ret['S'] = ret['S'].apply(lambda x: x if x != 17 else "None")
    ret = ret.reset_index(drop=True)
    if not is_historical:
        return ret, predict(i), True
    if is_historical:
        actual_seed = mdf_labindex.loc[team, 'S']
        avg_seed = 0
        denom = 0
        for i in range(55):
            if ret.loc[i,'S'] in range(1,17):
                avg_seed += ret.loc[i,'S'] * 1/ret.loc[i,'distance']**1
                denom += 1/ret.loc[i,'distance']**1
        if avg_seed < 1:
            avg_seed = "None"
        else:
            avg_seed = avg_seed/denom
        return ret, [avg_seed, actual_seed], False


def polish_main_df(df):
    df['Made Tourney'] = df['Made Tourney'].apply(lambda x: round((x * 100), 1))
    df = df.sort_values(by=['Made Tourney', 'Avg. Seed'], ascending=[False, True])
    df['Made Tourney'] = df['Made Tourney'].apply(lambda x: str(x) + "%")
    df.reset_index(inplace=True, drop=True)
    df.reset_index(inplace=True)
    df['index'] = df['index'] + 1
    df = df.rename(columns={'index':'Rank'})
    df['Team'] = df.Team.apply(lambda x: '<a href="' + x + '">' + x + "</a>")
    df['#1 Match'] = df['#1 Match'].apply(lambda x: '<a href="' + x + '">' + x + "</a>")
    df['#2 Match'] = df['#2 Match'].apply(lambda x: '<a href="' + x + '">' + x + "</a>")
    df['#3 Match'] = df['#3 Match'].apply(lambda x: '<a href="' + x + '">' + x + "</a>")
    for c in ['Avg. Seed', 'Most Likely Seed', 'Made Tourney']:
        df.rename(columns={c: '<a href="' + c + '">' + c + "</a>"}, inplace=True)
    return df

polish_main_df(write).to_csv('data/polished_main_df.csv')
df_curr.to_csv('data/df_curr.csv')
