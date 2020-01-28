# python version 3.8.0

# Import required packages
import requests
import json
import pull_data as api_puller
import data_sorter
import csv
import time_convertor
import pickle
from datetime import datetime
import simple_notifications as SimplyNotify

# global constants
PULL_API_DATA = False	 # pull data. if False reload data of last pull
EMAIL_NOTIFY = False       # flag to push notify to phone
# min value of the bet oppertunities max_value to prompt emailing notification
EMAIL_NOTIFY_THRESHHOLD = 1
H2H_WIN_ODDS_THRESHOLD = 2.0  # top odds threshold
H2H_SAFETY_ODDS_THRESHOLD = 1.4  # safety odds threshold
TOTAL_VALUE_THRESHOLD = 0.985  # Total value threshold
REGION_CODE = 'au'


def main():

    response_data = {'sports': [], 'odds_data': []}
    odds_jsons = []
    data_processor = []
    # sites exclude list
    exclude_sites = []
    # sites to use. Empty means use all avalible
    sites_best = []
    sites_safety = []

    results_print_statement = ""

    if PULL_API_DATA:
        # send api request for data for each sport
        api_grabber = api_puller.GetData()
        active_sports = ['americanfootball_ncaaf', 'americanfootball_nfl', 'basketball_euroleague', 'basketball_nba', 'basketball_ncaab', 'cricket_test_match', 'icehockey_nhl',
                         'mma_mixed_martial_arts', 'cricket_big_bash', 'rugbyleague_nrl', 'rugbyunion_six_nations', 'rugbyunion_super_rugby', 'tennis_atp_aus_open_singles', 'tennis_wta_aus_open_singles']

        for sport in active_sports:
            request_params = api_puller.SportOddsRequestParams(
                sport=sport, region=REGION_CODE, market='h2h')
            response_data['odds_data'].append(
                api_grabber.get_sport_odds(request_params))

        # save as .pickle so can be reloaded for testing. Saves api calls
        response_data['sports'] = active_sports
        pickle.dump(response_data, open("save.pickle", "wb"))
        pickle.dump(response_data, open("backup_pickles/save" + str(
            datetime.now().strftime('_%d_%Y_%m_%H_%M_%S_')) + REGION_CODE + ".pickle", "wb"))
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
        data_processor[count].check_for_h2h_odds_total_value(
            TOTAL_VALUE_THRESHOLD)
        #data_processor[i].check_for_h2h_odds_win_lose_thresholds(H2H_WIN_ODDS_THRESHOLD, H2H_SAFETY_ODDS_THRESHOLD)
        count = count + 1

    # print results
    for i in range(len(data_processor)):
        if len(data_processor[i].bet_opportunities['odds data']) > 0:
            results_print_statement = results_print_statement + 'Arbitrage opportunity for ' + \
                data_processor[i].sports_name + ' for the following: \n '
            for j, event in enumerate(data_processor[i].bet_opportunities['odds data']):
                results_print_statement = results_print_statement + "Match Details: " + str(event) + "  ||  Total odds 'value': " + str(data_processor[i].bet_opportunities['odds total value'][j]) + '  ||  Event Time: ' + str(
                    data_processor[i].bet_opportunities['start time'][j]) + "  ||  Time until: " + str(data_processor[i].bet_opportunities['time till start'][j]) + "\n"
        else:
            results_print_statement = results_print_statement + \
                'No Arbitrage opportunities for ' + \
                str(data_processor[i].sports_name)
        results_print_statement = results_print_statement + '\n \n '

    print(results_print_statement)

    if EMAIL_NOTIFY:
        for i in range(len(data_processor)):
            if data_processor[i].bet_opportunities['max value'] > EMAIL_NOTIFY_THRESHHOLD:
                # email notify and break out as emails bet oppurtunities for all sports anyway
                SimplyNotify.email(
                    'Free Money to be made', results_print_statement, 'lanebirmbetnotify@gmail.com')
                break

    # test code for creating csv
    # with open('data_test.csv', mode='w') as employee_file:
    # 	employee_writer = csv.writer(employee_file, dialect='excel')
    # 	employee_writer.writerow(data_processor.teams)
    # 	employee_writer.writerow(data_processor.h2h_odds)
    # 	employee_writer.writerow(data_processor.betting_sites)

    print("main end")


def get_sports():
    """ get sports call """

    api_grabber = api_puller.GetData()
    api_grabber.get_active_sports()
    print('sports.json updated')


if __name__ == '__main__':
    main()
    # get_sports()
