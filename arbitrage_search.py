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

# global constants
PULL_API_DATA = False  # pull data. if False reload data of last pull
H2H_WIN_ODDS_THRESHOLD = 2.0 # top odds threshold
H2H_SAFETY_ODDS_THRESHOLD = 1.75 # safety odds threshold
REGION_CODE = 'au'

def main():

	response_data = {'sports':[] , 'odds_data':[]}
	odds_jsons = []
	data_processor = []

	if PULL_API_DATA:
		# send api request for data for each sport
		api_grabber = api_puller.GetData()
		# full list excluding soccer = ['americanfootball_nfl', 'aussierules_afl','basketball_euroleague','basketball_nba','cricket_test_match','icehockey_nhl','mma_mixed_martial_arts', 'rugbyleague_nrl']
		active_sports = ['americanfootball_nfl','basketball_euroleague','basketball_nba','cricket_test_match','icehockey_nhl','mma_mixed_martial_arts']
		#active_sports = ['rugbyleague_nrl']
		
		for sport in active_sports:
			request_params = api_puller.SportOddsRequestParams(sport=sport, region=REGION_CODE, market='h2h')
			response_data['odds_data'].append(api_grabber.get_sport_odds(request_params))
			
		# save as .pickle so can be reloaded for testing. Saves api calls
		response_data['sports'] = active_sports
		pickle.dump(response_data, open( "save.pickle", "wb" ))
		pickle.dump(response_data, open( "backup_pickles/save" + str(datetime.now().strftime('_%d_%Y_%m_%H_%M_%S')) + REGION_CODE + ".pickle", "wb" ))   
	else:
		# reload last pull data

		#read response json from file
		# with open('json_dumps\odds.json', 'r') as odds_file:
		# 	response_data['odds_data'].append(json.load(odds_file))

		# read from pickle file
		response_data = pickle.load( open( "save.pickle", "rb" ) )

	# sites to use
	#sites_best = []
	#sites_safety = []
	sites_best = []
	sites_safety = []

	for i,odds in enumerate(response_data['odds_data']):
		# for each sport process response
		data_processor.append(data_sorter.DataProcessor())
		data_processor[i].filter_data(odds)
		data_processor[i].sort_max_h2h_odds(sites_best, sites_safety)
		data_processor[i].check_for_h2h_odds_win_lose_thresholds(H2H_WIN_ODDS_THRESHOLD, H2H_SAFETY_ODDS_THRESHOLD)


	# print results
	for i in range(len(data_processor)):
		if len(data_processor[i].bet_opportunities['odds data']) > 0:
			print('Arbitrage opportunity for', data_processor[i].sports_name, ' for the following: \n ')
			for j,event in enumerate(data_processor[i].bet_opportunities['odds data']):
				print("Match Details: ", event, '  ||  Event Time: ', data_processor[i].bet_opportunities['start time'][j], "  ||  Time until: ", data_processor[i].bet_opportunities['time till start'][j])
		else:
			print('No Arbitrage opportunities for ', data_processor[i].sports_name)
		print('\n \n ')

	
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


if __name__== '__main__':
	main()
	#get_sports()