# python version 3.8.0

# Import required packages
import requests
import json
import pull_data as api_puller
import data_sorter 
import csv
import time_convertor

# global constants
PULL_API_DATA = False  # pull data. if False reload data of last pull
H2H_ODDS_THRESHOLD = 1.8 # if both teams have avalible odds above this threshold will be counted as arbitrage bet opportunity

def main():

	odds_jsons = []
	data_processor = []
	active_sports = ['**loaded_from_file**']

	if PULL_API_DATA:
		# send api request for data for each sport
		api_grabber = api_puller.GetData()
		active_sports = ['americanfootball_nfl', 'aussierules_afl','basketball_euroleague','basketball_nba','cricket_test_match','icehockey_nhl','mma_mixed_martial_arts', 'rugbyleague_nrl']
		#active_sports = ['rugbyleague_nrl']
		
		for sport in active_sports:
			request_params = api_puller.SportOddsRequestParams(sport)
			odds_jsons.append(api_grabber.get_sport_odds(request_params))
	else:
		# reload last pull data

		#read response json from file
		with open('json_dumps\odds.json', 'r') as odds_file:
			odds_jsons.append(json.load(odds_file))


	for i,odds in enumerate(odds_jsons):
		# for each sport process response
		data_processor.append(data_sorter.DataProcessor())
		data_processor[i].filter_data(odds)
		data_processor[i].sort_max_h2h_odds()
		data_processor[i].check_for_h2h_odds_at_threshold(H2H_ODDS_THRESHOLD)

	for i in range(len(active_sports)):
		if len(data_processor[i].arbitrage_bet_opportunities['odds data']) > 0:
			print('Arbitrage opportunity for', active_sports[i], ' for the following: \n ')
			for j,event in enumerate(data_processor[i].arbitrage_bet_opportunities['odds data']):
				print("Match Details: ", event, '  ||  Event Time: ', data_processor[i].arbitrage_bet_opportunities['start time'][j], " ")
		else:
			print('No Arbitrage opportunities')
	print('\n \n ')

	
	# test code for creating csv
	# with open('data_test.csv', mode='w') as employee_file:
	# 	employee_writer = csv.writer(employee_file, dialect='excel')
	# 	employee_writer.writerow(data_processor.teams)
	# 	employee_writer.writerow(data_processor.h2h_odds)
	# 	employee_writer.writerow(data_processor.betting_sites)


	
	print("main end")




if __name__== '__main__':
	main()