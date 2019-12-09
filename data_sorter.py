# python version 3.8.0

# Import required packages
import time_convertor

def main():
	# shouldnt run this
	print("Main. Should be running this file directly")

class DataProcessor():
	def __init__(self):
		""" init """
		self.teams = []
		self.h2h_odds = []
		self.betting_sites = []
		self.max_h2h_odds = []
		self.start_time = {'datetime format':[] , 'string format':[]}
		self.arbitrage_bet_opportunities = {'odds data':[] , 'match index':[], 'start time':[]}

	def filter_data(self, json_data):
		""" process data to pull out just teams, sites and h2h odds of all events  """

		data = json_data['data']
		local_time_convertor = time_convertor.TimeConvertor()


		for event_data in data:
			# go through each event and save data

			# first need to get data for all avalible sites
			event_h2h_odds = []
			event_site_names = []
			for i, sites_data in enumerate(event_data['sites']):
				if len(sites_data['odds']['h2h']) > 2:
					# if more the 3 odds values (draw odds given) only take win loss odds
					event_h2h_odds.append([sites_data['odds']['h2h'][0], sites_data['odds']['h2h'][1]])
				else:
					event_h2h_odds.append(sites_data['odds']['h2h'])
				event_site_names.append(sites_data['site_nice'])
			
			# append event data
			self.teams.append(event_data['teams'])
			self.h2h_odds.append(event_h2h_odds)
			self.betting_sites.append(event_site_names)

			local_time_convertor.convert_to_AEST(event_data['commence_time'])
			self.start_time['string format'].append(local_time_convertor.local_time_string)
			self.start_time['datetime format'].append(local_time_convertor.local_time)

		# debug helper code
		# print(self.teams)
		# print(self.betting_sites)
		# print(self.h2h_odds)

	def sort_max_h2h_odds(self):
		"""  sort to get max odds offered for each team for all events. """

		for i,event in enumerate(self.teams):
			# for each event

			# init list of 2 dictonarys (1 for each team) that contains the max odds and the site for those odds
			self.max_h2h_odds.append({self.teams[i][0] : [0, "no site"], self.teams[i][1] : [0, "no site"]})

			for j,team in enumerate(self.teams[i]):
				# for each team
				for k,site_odds in enumerate(self.h2h_odds[i]):
					# for all odds find largest and save
					if site_odds[j] > self.max_h2h_odds[i][team][0]:
						self.max_h2h_odds[i][team] = [site_odds[j] , self.betting_sites[i][k]]
		
		#print('Finished finding max odds')

	def check_for_h2h_odds_at_threshold(self, min_h2h_alert_threshold = 2.0):
		"""  Alert if there is an event where odds are found for both teams of an event above the threshold """

		if len(self.max_h2h_odds) < 0:
			print('Have not sorted max h2h odds yet')
			return
		
		for i,event in enumerate(self.teams):
			# for each event check if max odds for both teams is above the threshold
			team_one_above = False
			team_two_above = False

			if self.max_h2h_odds[i][event[0]][0] > min_h2h_alert_threshold:
				team_one_above = True
			if self.max_h2h_odds[i][event[1]][0] > min_h2h_alert_threshold:
				team_two_above = True

			if team_one_above and team_two_above:
				#print('Found Arbitrage opportunity for event ', i)
				self.arbitrage_bet_opportunities['odds data'].append(self.max_h2h_odds[i])
				self.arbitrage_bet_opportunities['match index'].append(i)
				self.arbitrage_bet_opportunities['start time'].append(self.start_time['string format'][i])


if __name__== '__main__':
	main()