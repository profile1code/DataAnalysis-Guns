from matplotlib import pyplot as plt
import pandas as pd
import geopandas as gpd
import numpy as np
import os
from cse163_utils import assert_equals
import tests


def create_folders():
    '''This function creates the missing folders to avoid errors
    when saving images'''
    if not os.path.exists('Images'):
        os.mkdir('Images')

def get_us_map():
    '''This function creates the geopandas dataframe which contains
    geospacial data for the USA mainland'''
    states = gpd.read_file('cb_2014_us_state_5m.shp')

    remove_states = [
        'Puerto Rico', 'United States Virgin Islands', 'American Samoa',
        'Commonwealth of the Northern Mariana Islands', 'Guam', 'Hawaii',
        'Alaska', 'District of Columbia'
    ]
    index_remove = []
    for row in range(len(states)):
        if states.loc[row, 'NAME'] in remove_states:
            index_remove.append(row)
    return states.drop(index_remove, axis=0)

def plot_geodata(gdf, title, filename, death_column_name, state_column_name):
    gdf.plot(column = death_column_name, legend = True, cmap='Reds', edgecolor='grey')
    plt.title(title)
    plt.savefig('Images/' + filename)
    plt.clf()
    

    cell_data = gdf.nlargest(5, death_column_name)
    cell_data = cell_data.reset_index(drop=True)
    cell_d = []
    for row in range(len(cell_data)):
        cell_d.append(
            [cell_data.loc[row, state_column_name], cell_data.loc[row, death_column_name]])

    cell_data = keep_columns(cell_data, [state_column_name, death_column_name])
    colors = plt.cm.Reds(np.linspace(0, 0.5, 5))
    colour = []
    for x in range(5):
        colour.append([colors[x], colors[x]])

    fig, ax = plt.subplots()

    fig.patch.set_visible(False)
    ax.axis('off')

    ax.table(cellText=cell_data.values,
             colLabels=['State', 'Count'],
             cellColours=colour,
             loc='center')

    plt.savefig('Images/' + filename[: -4] + '_table.png')
    plt.clf()
    ax.axis('on')
    fig.patch.set_visible(True)

def heat_map_per_state(df, d_type, test = False):
    columns_remove = ['state', 'n_killed']
    df = keep_columns(df, columns_remove)

    if d_type == 'Incidents':
        df1 = df.groupby('state')['n_killed'].count()
    else:
        df1 = df.groupby('state')['n_killed'].sum()

    states = get_us_map()
    states = states.merge(df1, left_on='NAME', right_on='state')
    if test is False:
        plot_geodata(states, 'Total ' + d_type + ' By State (2013-2018)', 'per_state_map_' + d_type + '.png', 'n_killed', 'NAME')
    return states

def heat_map_per_capita_per_state(df, d_type, test = False):
    cols = ['state', 'n_killed']
    df = keep_columns(df, cols)

    if d_type == 'Incidents':
        df1 = df.groupby('state')['n_killed'].count()
    else:
        df1 = df.groupby('state')['n_killed'].sum()
    
    if test is True:
        population_data = get_2015_pop('Test_Data/test_population_data.csv')
    else:
        population_data = get_2015_pop('Populations_state.csv')
    
    population_data = population_data.merge(df1,
                                            left_on='Name',
                                            right_on='state')

    population_data['Per capita'] = population_data[
        'n_killed'] / population_data['Pop. 2015'] * 100000
    population_data = remove_columns(population_data,
                                     ['n_killed', 'Pop. 2015'])
    states = get_us_map()
    states = states.merge(population_data, left_on='NAME', right_on='Name')
    if test is False:
        plot_geodata(states, d_type + ' Per 100,000 Capita By State (2013-2018)', 'per_capita_per_state_map_' + d_type + '.png', 'Per capita', 'Name')

    return states

def age_gender_overall(df, type, test = False):
    columns_remove = [
        'participant_type', 'participant_gender', 'participant_age_group',
        'incident_characteristics'
    ]
    #Will drop lines that have incident information
    df = keep_columns(df, columns_remove)
    df = df.reset_index(drop=True)
    df.to_csv('age_gender.csv')
    maleadult = 0
    femaleadult = 0
    maleminor = 0
    femaleminor = 0

    gang_maleadult = 0
    gang_femaleadult = 0
    gang_maleminor = 0
    gang_femaleminor = 0
    
    for line in range(len(df)):
        participant_split = df.loc[line, 'participant_type'].split('|')
        gender_split = df.loc[line, 'participant_gender'].split('|')
        age_split = df.loc[line, 'participant_age_group'].split('|')

        

        participants = [item for item in participant_split if type in item]
        gender_groups = [item for item in gender_split if item != '']
        age_groups = [item for item in age_split if item != '']
        count_gang = 'gang' in df.loc[line, 'incident_characteristics'].lower()
        for str in participants:
            participant = str[0]
            gender_str = ''
            age_str = ''
            for item in gender_groups:
                if participant in item:
                    gender_str = item
            for item in age_groups:
                if participant in item:
                    age_str = item
            if gender_str != '' and age_str != '':
                gender = gender_str[3]
                age = age_str[3]
                if gender == 'M':
                    if age == 'T':
                        maleminor += 1
                        if count_gang:
                            gang_maleminor += 1
                    elif age == 'A':
                        maleadult += 1
                        if count_gang:
                            gang_maleadult += 1
                elif gender == 'F':
                    if age == 'T':
                        femaleminor += 1
                        if count_gang:
                            gang_femaleminor += 1
                    elif age == 'A':
                        femaleadult += 1
                        if count_gang:
                            gang_femaleadult += 1
    if test is False:
        plot_age_gender_overall(maleadult, maleminor, femaleadult, femaleminor,
                                gang_maleadult, gang_maleminor, gang_femaleadult, gang_femaleminor)
    return [maleadult, maleminor, femaleadult, femaleminor,
                            gang_maleadult, gang_maleminor, gang_femaleadult, gang_femaleminor]

def plot_age_gender_overall(ma, mm, fa, fm, gma, gmm, gfa, gfm):
    plt.bar(x=['Male (18+)', 'Male (12-17)', 'Female (18+)', 'Female (12-17)'],
            height=[ma, mm, fa, fm],
            label='All ' + type)
    plt.bar(x=['Male (18+)', 'Male (12-17)', 'Female (18+)', 'Female (12-17)'],
            height=[gma, gmm, gfa,gfm], label='Gang Involvement')
    plt.title('Total ' + type)
    plt.legend()
    plt.savefig('Images/' + type + '_by_age_gender.png')
    plt.clf()

def finding_gun_types(df, test = False):

    types = {}
    cols = ['gun_type']
    df = keep_columns(df, cols)
    df = df.reset_index(drop=True)
    for line in range(len(df)):
        data = df.loc[line, 'gun_type']
        data = clean_data(data)
        for item in data:
            if item not in types:
                types[item] = 0
            types[item] += 1
    sort = sorted(types.items(), key=lambda item: item[1], reverse=True)

    df1 = pd.DataFrame()
    gun_types = []
    gun_num = []
    for x in sort[0:10]:
        gun_types.append(x[0])
        gun_num.append(x[1])
    df1['Types'] = gun_types
    df1['Occurences'] = gun_num
    if test == True:
        return df1
    else:
        colors = plt.cm.BuPu(np.linspace(0, 0.5, len(df1['Types'])))
        colour = []
        for x in range(len(colors)):
            colour.append([colors[x], colors[x]])

        fig, ax = plt.subplots()

        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')

        ax.table(cellText=df1.values,
                colLabels=df1.columns,
                cellColours=colour,
                loc='center')

        fig.tight_layout()

        plt.savefig('Images/' + 'gun_types.png')
        plt.clf()


def graph_over_time(df,
                    states,
                    violence,
                    test=False,
                    file='Populations_state.csv'):
    """
    Generates a line graph of either incidents or deaths over time PER CAPITA
    using a seperate dataset for state population.Takes in the gun violence
    dataframe, a list of all US states, the type of graph to be generated 
    (violence is either incidents or deaths), a boolean for testing, and 
    the state populations filename.
    """
    cols = ['state', 'date', 'n_killed']
    df = keep_columns(df, cols)
    df = df.reset_index(drop=True)
    fig, ax1 = plt.subplots()
    data_save = []
    populations = get_2015_pop(file).set_index('Name')
    for state in states:
        drop = []
        for line in range(len(df)):
            if df.loc[line, 'state'] != state:
                drop.append(line)
        df1 = df
        df1 = df1.drop(drop, axis=0)

        df1 = remove_columns(df1, ['state'])
        df1.to_csv('date.csv')
        df.to_csv('date_total.csv')
        ts = pd.read_csv('date.csv', index_col='date', parse_dates=True)
        ts_total = pd.read_csv('date_total.csv', index_col='date', parse_dates=True)
        #Incidents vs Deaths plotting
        ts_total.resample('M')['n_killed'].sum()
        if violence == 'Incidents':
            ts = (ts.resample('M')['n_killed'].count() /
                  populations.loc[state, 'Pop. 2015'] * 100000 / ts_total.resample('M')['n_killed'].count())
            data_save.append(ts)
            plt.plot(ts, label=state)
        else:
            ts = (ts.resample('M')['n_killed'].sum() /
                  populations.loc[state, 'Pop. 2015'] * 100000 / ts_total.resample('M')['n_killed'].sum())
            data_save.append(ts)
            plt.plot(ts, label=state)
    #Test case
    if test == False:
        plt.legend()
        plt.title('Top 3 States for ' + violence + ' Over Time')
        plt.savefig('Images/' + violence + '_over_time_', bbox_inches='tight')
        plt.clf()
    else:
        return data_save


def remove_columns(df, column_list):
    'Helper method which removes columns in the list sent'
    df = df.drop(columns=column_list)
    df = df.dropna()
    return df


def keep_columns(df, columns):
    drop = []
    for column in df.columns:
        if column not in columns:
            drop.append(column)
    df = df.drop(columns=drop)
    df = df.dropna()
    return df


def clean_data(data):
    guns = data.split('|')
    new_guns = []
    for item in guns:
        if 'unknown' not in item.lower() and len(item) > 0:
            new_guns.append(item.split(':')[-1])
    return new_guns


def get_2015_pop(csv):
    columns_remove = [
        'Pop. 1990', 'Pop. 2000', 'Pop. 2010', 'Pop. 2020', 'Pop. 2021',
        'Change 2020-21'
    ]
    population_data = pd.read_csv(csv)
    population_data['Pop. 2015'] = 0
    for row in range(len(population_data)):
        new_2010 = population_data.loc[row, 'Pop. 2010']
        if ',' in str(new_2010): 
            new_2010 = new_2010.replace(',', '')
        new_2020 = population_data.loc[row, 'Pop. 2020']
        if ',' in str(new_2020): 
            new_2020 = new_2020.replace(',', '')
        population_data.loc[row,
                            'Pop. 2015'] = (int(new_2020) + int(new_2010)) / 2
    population_data = remove_columns(population_data, columns_remove)

    return population_data


def main():
    create_folders()
    columns = [
        'incident_id', 'date', 'state', 'city_or_county', 'address',
        'n_killed', 'n_injured', 'incident_url', 'source_url',
        'incident_url_fields_missing', 'congressional_district', 'gun_stolen',
        'gun_type', 'incident_characteristics', 'latitude',
        'location_description', 'longitude', 'n_guns_involved', 'notes',
        'participant_age', 'participant_age_group', 'participant_gender',
        'participant_name', 'participant_relationship', 'participant_status',
        'participant_type', 'sources', 'state_house_district',
        'state_senate_district'
    ]
    
    #create_graphs()
    test_data()


def create_graphs():
    df = pd.read_csv('shootings.csv')

    #heat_map_per_state(df, 'Incidents')
    #heat_map_per_state(df, 'Deaths')
    #heat_map_per_capita_per_state(df, 'Incidents')
    #heat_map_per_capita_per_state(df, 'Deaths')
    #age_gender_overall(df, 'Victim')
    #age_gender_overall(df, 'Subject-Suspect')
    #finding_gun_types(df)
    incident_states = ['Delaware', 'Louisiana', 'South Carolina']
    death_states = ['Louisiana', 'Mississippi', 'Alabama']
    graph_over_time(df, incident_states, 'Incidents')
    graph_over_time(df, death_states, 'Deaths')


def test_data():
    missing_data = pd.read_csv('Test_Data/test_missing_data.csv')
    agv = pd.read_csv('Test_Data/test_agv.csv')
    over_time = pd.read_csv('Test_Data/test_over_time.csv')
    #tests.test_gpd_data(missing_data)
    #tests.test_gendervictim_data(agv)
    tests.test_graph_over_time(over_time)
    #tests.test_finding_gun_types(over_time)
    

if __name__ == '__main__':
    main()
