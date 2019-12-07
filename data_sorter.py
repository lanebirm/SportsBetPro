# python version 3.8.0

# Import required packages
import requests
import json
import pull_data as api_puller
import csv

def main():
	api_grabber = api_puller.GetData(False)
	#APIDataGrabber.activeSports()

	#test for mma
	# cricket_params = api_puller.SportOddsRequestParams('mma_mixed_martial_arts')
	# api_grabber.GetSportOdds(cricket_params)

def main_dummy():
	"""  dummy main for testing based on presaved API response. """
	#read response json from file
	with open('json_dumps\odds_example.json', 'r') as odds_file:
		odds_json = json.load(odds_file)
	#print(odds_json)

	data_processor = DataProcessor()
	data_processor.process_response(odds_json)
	
	with open('data_test.csv', mode='w') as employee_file:
		employee_writer = csv.writer(employee_file, dialect='excel')
		employee_writer.writerow(data_processor.teams)
		employee_writer.writerow(data_processor.odds)
		employee_writer.writerow(data_processor.betting_sites)

class DataProcessor():
	def __init__(self):
		""" init """
		self.teams = []
		self.odds = []
		self.betting_sites = []

	def process_response(self, json_data):
		EVENT_INDEX = 1 
		
		data = json_data['data']
		self.teams.extend(data[EVENT_INDEX]['teams'])
		for i, sites_data in enumerate(data[EVENT_INDEX]['sites']):
			self.odds.append(sites_data['odds']['h2h'])
			self.betting_sites.append(sites_data['site_nice'])

		print(self.teams)
		print(self.betting_sites)
		print(self.odds)

		







if __name__== '__main__':
	#main()
	main_dummy()