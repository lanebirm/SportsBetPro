# python version 3.8.0

# Import required packages
import requests
import json

def main():
	APIDataGrabber = getData(False)
	#APIDataGrabber.activeSports()

	#test for mma
	cricket_params = sportOddsRequestParams('mma_mixed_martial_arts')
	APIDataGrabber.getSportOdds(cricket_params)





class getData():
	"""docstring for getData"""
	def __init__(self, arg):
		super(getData, self).__init__()
		# dummy arg for now
		self.arg = arg
		
	def activeSports(self):
		print('Starting Sports Request')

		# https://api.the-odds-api.com/v3/sports/?apiKey=4e28f0f30c120627544a89a7a51977a5
		resp = requests.get('https://api.the-odds-api.com/v3/sports',
			headers={'Content-Type':'application/json'},
			params={'sport':'cricket_test_match', 'region':'au', 'api_key': '4e28f0f30c120627544a89a7a51977a5'} )
		print(resp.json())

		#dump response json to file
		with open('json_dumps\sports.json', 'w') as f:
			json.dump(resp.json(), f)

		print('Finish Sports Request')
		

	def getSportOdds(self, sportOddsRequestParams):
		print('Starting Sports Request')

		resp = requests.get(sportOddsRequestParams.request_url,
			headers = {'Content-Type':'application/json'},
			params = sportOddsRequestParams.params )
		print(resp.json())

		#dump response json to file
		with open('json_dumps\odds.json', 'w') as f:
			json.dump(resp.json(), f)

		print('Finish Sports Request')

class sportOddsRequestParams():
	"""class for data structures for request parameters"""
	def __init__(self, sport='not set', region='au', market='h2h'):
		#setup structure
		self.params = {}
		self.params['api_key'] = '4e28f0f30c120627544a89a7a51977a5'
		self.params['region'] = region
		self.params['sport'] = sport
		self.params['mkt'] = market #default to h2h

		self.request_url = 'https://api.the-odds-api.com/v3/odds'

	def updateParams(self, sport, region='au', market='h2h'):
		self.params['sport'] = sport
		self.params['sport'] = region
		self.params['sport'] = market





if __name__== '__main__':
	main()
