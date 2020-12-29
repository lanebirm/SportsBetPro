# python version 3.8.0
# Author: Lane Birmingham

import numpy as np
import pandas as pd

def create_print_statement(data_processors):
    # results print statement
    results_print_statement = ""
    for i in range(len(data_processors)):
        if len(data_processors[i].bet_opportunities['odds data']) > 0:
            results_print_statement = results_print_statement + 'Arbitrage opportunity for ' + \
                data_processors[i].sports_name + ' for the following: \n '
            results_print_statement = results_print_statement + 'Max "value" of: ' + \
                str(data_processors[i].bet_opportunities['max value']) + '\n'
            for j, event in enumerate(data_processors[i].bet_opportunities['odds data']):
                results_print_statement = results_print_statement + "Match Details: " + str(event) + "  ||  Total odds 'value': " + str(data_processors[i].bet_opportunities['odds total value'][j]) + '  ||  Event Time: ' + str(
                    data_processors[i].bet_opportunities['start time'][j]) + "  ||  Time until: " + str(data_processors[i].bet_opportunities['time till start'][j]) + "\n"
        else:
            results_print_statement = results_print_statement + \
                'No Arbitrage opportunities for ' + \
                str(data_processors[i].sports_name)
        results_print_statement = results_print_statement + '\n \n '
    
    return results_print_statement

def create_dfs(data_processors):
    # create panda dataframes for each sport

    # lists per data_processor class
    sports_names = []
    sports_max_values = []
    has_values_flags = []

    # lists per data_processor of lists of opportunities per event
    odds_data_sets_one = []
    team_sets_one = []
    sites_sets_one = []
    odds_data_sets_two = []
    team_sets_two = []
    sites_sets_two = []
    odds_total_value_sets = []
    start_time_sets = []
    time_until_sets = []

    # Output data farmes. Frame per sport
    sport_dfs = []
    
    titles = ["Total Odds Value", "Team1", "Site1", "Odds1", "Team2", "Site2", "Odds2", "Event Time", "Time Unitl"]

    # results data lists
    for i in range(len(data_processors)):
        if len(data_processors[i].bet_opportunities['odds data']) > 0:
            # append results for data frame
            has_values_flags.append(True)
            sports_names.append(data_processors[i].sports_name)
            sports_max_values.append(data_processors[i].bet_opportunities['max value'])

            odds_total_value_sets.append(data_processors[i].bet_opportunities['odds total value'])
            start_time_sets.append(data_processors[i].bet_opportunities['start time'])
            time_until_sets.append(data_processors[i].bet_opportunities['time till start'])

            #need to got through each odds data event
            events_odds_set = []
            events_sites_set = []
            events_teams_set = []
            events_odds_set_2 = []
            events_sites_set_2 = []
            events_teams_set_2 = []
            for j, event in enumerate(data_processors[i].bet_opportunities['odds data']):
                teams = []
                sites = []
                odds = []
                for keys in event:
                    teams.append(keys)
                    sites.append(event[keys][1]) # Site name
                    odds.append(event[keys][0]) # odds value
                
                events_teams_set.append(teams[0])
                events_sites_set.append(sites[0])
                events_odds_set.append(odds[0])
                events_teams_set_2.append(teams[1])
                events_sites_set_2.append(sites[1])
                events_odds_set_2.append(odds[1])
            
            
            odds_data_sets_one.append(events_odds_set)
            sites_sets_one.append(events_sites_set)
            team_sets_one.append(events_teams_set)
            odds_data_sets_two.append(events_odds_set_2)
            sites_sets_two.append(events_sites_set_2)
            team_sets_two.append(events_teams_set_2)
        else:
            sports_names.append(data_processors[i].sports_name)
            sports_max_values.append(0.0)
            has_values_flags.append(False)

    count = 0
    for i in range(len(sports_names)):
        if has_values_flags[i]:
            array = np.array([odds_total_value_sets[count], team_sets_one[count], sites_sets_one[count], odds_data_sets_one[count], team_sets_two[count], sites_sets_two[count], odds_data_sets_two[count], start_time_sets[count], time_until_sets[count]])
            df = pd.DataFrame(array, index=titles)
            df_transposed = df.T 
            #TODO sort out / df_transposed.sort_values("Total Odds Value", axis='columns', ascending=False, inplace=True, kind='quicksort', na_position='last')
            count = count + 1
        else:
            # empty df for the sport
            array = np.array(["", "", ""])
            df_transposed = pd.DataFrame(array)

        sport_dfs.append(df_transposed)
       

    return sport_dfs, sports_names, sports_max_values, has_values_flags