# Import required packages
import requests
import json


class getData(object):
	"""docstring for getData"""
	def __init__(self, arg):
		super(getData, self).__init__()
		self.arg = arg
		
	def activeSports():
		print('Starting Request')
		# https://api.the-odds-api.com/v3/sports/?apiKey=4e28f0f30c120627544a89a7a51977a5
		resp = requests.get('https://api.the-odds-api.com/v3/sports',
			headers={'Content-Type':'application/json'},
			params={'api_key': '4e28f0f30c120627544a89a7a51977a5' } )
		print(resp.json())
		print('Finish')


getData.activeSports()