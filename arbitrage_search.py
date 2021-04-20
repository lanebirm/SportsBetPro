#!/usr/bin/env python3
# Author: Lane Birmingham

# Import required packages
import requests
import json
import pull_data as api_puller
import data_sorter
import csv
import time_convertor
import time
import pickle
import pandas as pd
from datetime import datetime
import simple_notifications as SimplyNotify
import main_variables
import helper_functions as functions
import bet_web_scrap


def main(check_type=0):
    variables = main_variables.MainVariables(check_type)
    if arbitrage_check(variables, check_type):
        print("Successfully run")
    else:
        print("arbitrage check failed")


def arbitrage_check(variables, check_type):

    response_data = {'sports': [], 'odds_data': []}
    odds_jsons = variables.odds_jsons
    data_processor = variables.data_processor
    # sites exclude list
    exclude_sites = variables.exclude_sites
    # sites to use. Empty means use all avalible
    sites_best = variables.sites_best
    sites_safety = variables.sites_safety
    # exclusion list for sports that "max value" is used to trigger emails
    sports_name_exclusion = variables.sports_name_exclusion

    results_print_statement = ""

    # get OddsAPI data
    if variables.pull_api_data:
        # send api request for data for each sport
        api_grabber = api_puller.GetData()
        # Get active sports
        api_grabber.get_active_sports()

        # get active sports name
        active_sports_keys = []
        sports_nice = []
        sports_name_data = api_grabber.get_active_sports()
        for sport_name in sports_name_data['data']:
            active_sports_keys.append(sport_name['key'])
            sports_nice.append(sport_name['title'])

        fetched_sports = []
        fetched_sports_nice = []
        for i, sport in enumerate(active_sports_keys):
            if (sport not in variables.sports_names_not_to_pull):
                add_sport = True
                # Now check if sport contains any of exclude keyword
                for keyword in variables.sports_ignoring_keywords:
                    if keyword in sport:
                        add_sport = False
                        break
                if add_sport:
                    fetched_sports.append(sport)
                    fetched_sports_nice.append(sports_nice[i])
                    request_params = api_puller.SportOddsRequestParams(
                        sport=sport, region=variables.region_code, market='h2h')
                    response_data['odds_data'].append(
                        api_grabber.get_sport_odds(request_params))

        # save as .pickle so can be reloaded for testing. Saves api calls
        response_data['sports'] = fetched_sports
        response_data['sports_nice'] = fetched_sports_nice
        pickle.dump(response_data, open("save.pickle", "wb"))
        pickle.dump(response_data, open("backup_pickles/save" + str(
            datetime.now().strftime('_%d_%Y_%m_%H_%M_%S_')) + variables.region_code + ".pickle", "wb"))
    else:
        # reload last pull data
        # read from pickle file
        response_data = pickle.load(open("save.pickle", "rb"))

    web_scrap_df = pd.DataFrame(columns=["site_nice", "last_update", "odds.h2h",
                                         "odds.h2h_lay", "sport_nice", "commence_time", "teams", "teams_string"])
    if variables.web_scrap_data:
        # use web scrapper to generate pandas dataframe with additional data
        WS = bet_web_scrap.WebScrapper()
        WS.scrap_all_links()
        web_scrap_df = WS.result_df.copy()

    count = 0
    for i, odds in enumerate(response_data['odds_data']):
        # for each sport process response
        if len(odds['data']) < 1:
            continue
        data_processor.append(data_sorter.DataProcessor())
        # restructure OddsAPI data for multi source format
        json_data = odds["data"]
        for event in json_data:
            event["team1"] = event['teams'][0]
            event["team2"] = event['teams'][1]
        data_df = pd.json_normalize(json_data, record_path=['sites'], meta=[
                                    'sport_nice', 'commence_time', 'team1', 'team2'])

        teams = []
        odds_h2h = []

        for j in range(len(data_df["team1"].values)):
            temp_dict = {data_df["team1"][j]:data_df["odds.h2h"][j][0] , data_df["team2"][j]:data_df["odds.h2h"][j][1]}
            sorted_keys = sorted(temp_dict.keys())

            teams.append([sorted_keys[0], sorted_keys[1]])
            odds_h2h.append([temp_dict[sorted_keys[0]], temp_dict[sorted_keys[1]]])
        
        data_df["teams"] = teams 
        data_df["odds.h2h"] = odds_h2h

        data_df["teams_string"] = data_df["team1"] + " " + data_df["team2"]
        data_df.drop(["site_key", "team1", "team2"], axis=1, inplace=True)

        # append web scrapped data for the current sport
        data_df = data_df.append(web_scrap_df.loc[web_scrap_df["sport_nice"] == data_df['sport_nice'][0]], ignore_index=True)

        data_processor[count].filter_df_data(data_df)
        data_processor[count].sort_max_h2h_odds(
            sites_best, sites_safety, exclude_sites)
        data_processor[count].generate_odds_total_value()
        if check_type == 0:
            data_processor[count].check_for_h2h_odds_total_value(
                variables.total_value_threshold)
        elif check_type == 1:
            data_processor[count].check_for_h2h_odds_win_lose_thresholds(
                variables.h2h_win_odds_threshold, variables.h2h_win_odds_threshold)
        else:
            print("Invalid check_type")
            return False

        count = count + 1

    # Emailing + print with dfs
    max_value_of_intrest = variables.email_notify_threshold
    value_threshold_found = False
    for i in range(len(data_processor)):
        # Check sports value exclusion list if max value is of intrest
        if not (data_processor[i].sports_name in sports_name_exclusion):
            if data_processor[i].bet_opportunities['max value'] > max_value_of_intrest:
                value_threshold_found = True
                max_value_of_intrest = data_processor[i].bet_opportunities['max value']

    msg = SimplyNotify.MIMEMultipart()
    results_print_statement = None

    if variables.print_data_frames:
        # create data frame per table
        sports_names = []
        sports_max_values = []
        has_values_flags = []
        sports_dataframes, sports_names, sports_max_values, has_values_flags = functions.create_dfs(
            data_processor)

        msg.attach(SimplyNotify.MIMEText(
            "Max value of: " + str(max_value_of_intrest) + "\n"))
        end_string = ""
        for i, dataframe in enumerate(sports_dataframes):
            # setup print for email
            if has_values_flags[i]:
                results_dataframe_email_print = "\n " + sports_names[i]
                results_dataframe_email_print = results_dataframe_email_print + ' max "value" of: ' + \
                    str(sports_max_values[i]) + '\n' + '\n'

                msg.attach(SimplyNotify.MIMEText(
                    results_dataframe_email_print))

                html = """\
                    <html>
                    <head></head>
                    <body>
                        {0}
                    </body>
                    </html>
                    """.format(dataframe.to_html(render_links=True))
                table_as_string = SimplyNotify.MIMEText(html, 'html')

                msg.attach(table_as_string)

            else:
                end_string = end_string + \
                    '\nNo Arbitrage opportunities for ' + \
                    str(sports_names[i]) + '\n'

            results_dataframe_email_print = ""
            results_dataframe_email_print = results_dataframe_email_print + '\n '
        msg.attach(SimplyNotify.MIMEText(
            end_string))
        print(sports_dataframes)
    else:
        results_print_statement = functions.create_print_statement(
            data_processor)
        print(results_print_statement)

    if variables.email_notify:
        # email notify and break out as emails bet oppurtunities for all sports anyway
        if value_threshold_found:
            if variables.print_data_frames:
                for emails in variables.email_list:
                    SimplyNotify.email(
                        'Free Money to be made', emails, input_msg=msg)
            else:
                for emails in variables.email_list:
                    SimplyNotify.email(
                        'Free Money to be made', emails, results_print_statement)

    return True


def get_sports():
    """ get sports call """

    api_grabber = api_puller.GetData()
    api_grabber.get_active_sports()
    print('sports.json updated')


if __name__ == '__main__':
    call_type = {"total_value_check": 0, "win_lose_threshold": 1}
    main(call_type["total_value_check"])

    # get_sports()
