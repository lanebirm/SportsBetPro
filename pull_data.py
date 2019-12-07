# python version 3.8.0

# Import required packages
import requests
import json

def main():
	APIGrabber = getData(False)
	APIGrabber.activeSports()

class getData():
	"""docstring for getData"""
	def __init__(self, arg):
		super(getData, self).__init__()
		# dummy arg for now
		self.arg = arg
		
	def activeSports(self):
		print('Starting Request')
		# https://api.the-odds-api.com/v3/sports/?apiKey=4e28f0f30c120627544a89a7a51977a5
		resp = requests.get('https://api.the-odds-api.com/v3/sports',
			headers={'Content-Type':'application/json'},
			params={'api_key': '4e28f0f30c120627544a89a7a51977a5' } )
		print(resp.json())
		print('Finish')
		input('press enter to exit')


if __name__== '__main__':
	main()
