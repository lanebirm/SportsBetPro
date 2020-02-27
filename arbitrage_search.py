# python version 3.8.0
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
from datetime import datetime
import simple_notifications as SimplyNotify
import main_variables
import search_helper_functions as functions

def main():
    variables = main_variables.MainVariables()
    query(variables)

def query(variables):

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

    if variables.pull_api_data:
        # send api request for data for each sport
        api_grabber = api_puller.GetData()
        active_sports = ['americanfootball_ncaaf', 'americanfootball_nfl', 'basketball_euroleague', 'basketball_nba', 'basketball_ncaab', 'cricket_test_match', 'icehockey_nhl',
                         'mma_mixed_martial_arts', 'cricket_big_bash', 'rugbyunion_six_nations', 'rugbyunion_super_rugby','rugbyunion_premiership_rugby','cricket_odi']

        for sport in active_sports:
            request_params = api_puller.SportOddsRequestParams(
                sport=sport, region=variables.region_code, market='h2h')
            response_data['odds_data'].append(
                api_grabber.get_sport_odds(request_params))

        # save as .pickle so can be reloaded for testing. Saves api calls
        response_data['sports'] = active_sports
        pickle.dump(response_data, open("save.pickle", "wb"))
        pickle.dump(response_data, open("backup_pickles/save" + str(
            datetime.now().strftime('_%d_%Y_%m_%H_%M_%S_')) + variables.region_code + ".pickle", "wb"))
    else:
        # reload last pull data
        # read from pickle file
        response_data = pickle.load(open("save.pickle", "rb"))

    count = 0

    for odds in response_data['odds_data']:
        # for each sport process response
        if len(odds['data']) < 1:
            continue
        data_processor.append(data_sorter.DataProcessor())
        data_processor[count].filter_data(odds)
        data_processor[count].sort_max_h2h_odds(
            sites_best, sites_safety, exclude_sites)
        data_processor[count].generate_odds_total_value()
        #data_processor[count].check_for_h2h_odds_total_value(
         #  variables.total_value_threshold)
        data_processor[count].check_for_h2h_odds_win_lose_thresholds(variables.h2h_win_odds_threshold, variables.h2h_win_odds_threshold)
        count = count + 1

    results_print_statement = functions.create_print_statement(data_processor)

    # Data Frames
    msg = SimplyNotify.MIMEMultipart()
    if variables.print_data_frames:
        # create data frame per table
        sports_names = []
        sports_max_values = []
        has_values_flags =[]
        sports_dataframes, sports_names, sports_max_values, has_values_flags = functions.create_dfs(data_processor)

        results_dataframe_email_print = ""
        for i, dataframe in enumerate(sports_dataframes):
            # setup print for email
            if has_values_flags[i]:
                results_dataframe_email_print = results_dataframe_email_print + 'Arbitrage opportunity for ' + \
                    sports_names[i] + ' for the following: \n '
                results_dataframe_email_print = results_dataframe_email_print + 'Max "value" of: ' + \
                    str(sports_max_values[i]) + '\n' + '\n'

                msg.attach(SimplyNotify.MIMEText(results_dataframe_email_print))
                
                html = """\
                    <html>
                    <head></head>
                    <body>
                        {0}
                    </body>
                    </html>
                    """.format(dataframe.to_html())
                table_as_string = SimplyNotify.MIMEText(html, 'html')

                msg.attach(table_as_string)

            else:
                results_dataframe_email_print = results_dataframe_email_print + \
                    'No Arbitrage opportunities for ' + str(sports_names[i]) + '\n'
                msg.attach(SimplyNotify.MIMEText(results_dataframe_email_print))

            results_dataframe_email_print = ""
            results_dataframe_email_print = results_dataframe_email_print + '\n \n '
    else:
        print(results_print_statement)

    if variables.email_notify:
        for i in range(len(data_processor)):
            # Check sports value exclusion list if max value is of intrest
            if not (data_processor[i].sports_name in sports_name_exclusion):
                if data_processor[i].bet_opportunities['max value'] > variables.email_notify_threshold:
                    # email notify and break out as emails bet oppurtunities for all sports anyway
                    if variables.print_data_frames:
                        for emails in variables.email_list:
                            SimplyNotify.email(
                                'Free Money to be made', emails, input_msg=msg)
                    else:
                        for emails in variables.email_list:
                            SimplyNotify.email(
                                'Free Money to be made', emails, results_print_statement)

                    break

    print("main end")

    # test code for creating csv
    # with open('data_test.csv', mode='w') as employee_file:
    #   employee_writer = csv.writer(employee_file, dialect='excel')
    #   employee_writer.writerow(data_processor.teams)
    #   employee_writer.writerow(data_processor.h2h_odds)
    #   employee_writer.writerow(data_processor.betting_sites)

def get_sports():
    """ get sports call """

    api_grabber = api_puller.GetData()
    api_grabber.get_active_sports()
    print('sports.json updated')


def query_loop(duration_mins, interval_mins):
    """ function to call the main function every mins_interval """
    interval_in_secs = interval_mins*60
    duration_in_seconds = duration_mins*60

    t = time.time()
    while True:
        # call main function
        time_before_main = time.time()
        main()
        print('\n \n')

        time_for_main = time.time() - time_before_main

        current_interval_sub_main = interval_in_secs - time_for_main

        duration_in_seconds = duration_in_seconds - current_interval_sub_main - time_for_main

        # if waiting another interval will run till later then given duration finish looping now
        if duration_in_seconds < 0:
            break

        # sleep for the interval_in_secs
        if current_interval_sub_main <= 0:
            current_interval_sub_main = 0.01
        time.sleep(current_interval_sub_main)

    elapsed = time.time() - t
    print('Time taken looping ' + str(elapsed))
    print('End of query loop')

if __name__ == '__main__':
    main()
    # query_loop(0.6, 0.2)
    # get_sports()
