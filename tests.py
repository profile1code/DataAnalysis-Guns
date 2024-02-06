from cse163_utils import assert_equals
import pandas as pd
import geopandas as gpd
import main

def test_gpd_data(gpd):
        '''This method tests the functions heat_map_per_state() and
        hea_map_per_capita_per_state and checks whether they are returning
        the expected data '''
        incidents = main.heat_map_per_state(gpd, 'Incidents', True)
        compare = sum(pd.Series([1, 2]).to_list())
        assert_equals(compare, sum(incidents['n_killed'].to_list()))

        deaths = main.heat_map_per_state(gpd, 'Deaths', True)
        compare = sum(pd.Series([200, 150]).to_list())
        assert_equals(compare, sum(deaths['n_killed'].to_list()))

        incidents_per_capita = main.heat_map_per_capita_per_state(gpd, 'Incidents', True)
        #50000, 100000 is the result as it is number of deaths per 100000 people
        compare = sum(pd.Series([2 / 2  * 100000 , 1 / 1* 100000]).to_list())
        assert_equals(compare, sum(incidents_per_capita['Per capita'].to_list()))

        deaths_per_capita = main.heat_map_per_capita_per_state(gpd, 'Deaths', True)
        compare = sum(pd.Series([200 / 2 * 100000 , 150 / 1 * 100000]).to_list())
        assert_equals(compare, sum(deaths_per_capita['Per capita'].to_list()))

def test_gendervictim_data(df):
        '''This function tests the age_gender_overall function in main.py's
        values to confirm the correct numbers are being plotted'''
        values_victim = main.age_gender_overall(df, 'Victim', True)
        values_suspect = main.age_gender_overall(df, 'Subject-Suspect', True)
        compare_victim = [7, 1, 1, 0, 3, 0, 0, 0]
        compare_suspect = [3, 0, 1, 0, 0, 0, 1, 0]
        for index in range(len(values_victim)):
            assert_equals(compare_victim[index], values_victim[index])
            assert_equals(compare_suspect[index], values_suspect[index])

def test_graph_over_time(df):
    '''This function tests the function graph_over_time() in main'''
    states = ['Pennsylvania', 'Ohio', 'California']
    data_deaths = main.graph_over_time(df, states, 'Deaths', True, 'Test_Data/test_population_data.csv')
    data_incidents = main.graph_over_time(df, states, 'Incidents', True, 'Test_Data/test_population_data.csv')
    compare_deaths = [[200000 / 6, 400000 / 12, 600000 / 18], [100000 / 6, 200000 / 12, 300000 / 18], [50000 / 6, 100000 / 12, 150000 / 18]]
    compare_incidents = [[100000 / 3, 100000 / 3, 200000 / 6], [50000 / 3, 50000 / 3, 100000 / 6], [25000 / 3, 25000 / 3, 50000 / 6]]

    for state in range(len(states)):
          for item in range(len(data_deaths[state])):
            assert_equals(compare_deaths[state][item], data_deaths[state][item])
            assert_equals(compare_incidents[state][item], data_incidents[state][item])

def test_finding_gun_types(df):
    data = main.finding_gun_types(df, True)
    data = data.set_index('Types')
    print(data)
    compare = pd.DataFrame([['Handgun', 2], ['9mm', 4], ['Rifle', 1]], columns = ['Types', 'Occurences'])
    for row in range(len(compare)):
         compare_gun = compare.loc[row, 'Types']
         compare_val = compare.loc[row, 'Occurences']
         assert_equals(compare_val, data.loc[compare_gun, 'Occurences'])
                
          
    

