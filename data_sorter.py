# python version 3.8.0
# Author: Lane Birmingham

# Import required packages
import time_convertor
from datetime import datetime


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
        self.max_safety_odds = []
        self.odds_total_value = []
        self.sports_name = ''
        self.start_time = {'datetime format': [],
                           'string format': [], 'time till start': []}
        self.bet_opportunities = {'odds data': [], 'match index': [], 'start time': [
        ], 'time till start': [], 'odds total value': [], 'max value': 0}

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
                # if more the 3 odds values (draw odds given) only take win loss odds
                odds_one = sites_data['odds']['h2h'][0]
                odds_two = sites_data['odds']['h2h'][1]
                if sites_data['site_nice'] == 'Betfair':
                    # Bet exchange site. Need to adjust odds assuming 5% of profit is taken
                    odds_one = odds_one - ((odds_one - 1)*0.05)
                    odds_two = odds_two - ((odds_two - 1)*0.05)

                event_h2h_odds.append([odds_one, odds_two])
                event_site_names.append(sites_data['site_nice'])

            # append event data
            self.teams.append(event_data['teams'])
            self.h2h_odds.append(event_h2h_odds)
            self.betting_sites.append(event_site_names)

            local_time_convertor.convert_to_AEST(event_data['commence_time'])
            self.start_time['string format'].append(
                local_time_convertor.local_time_string)
            self.start_time['datetime format'].append(
                local_time_convertor.local_time)
            self.start_time['time till start'].append(
                local_time_convertor.time_until)

        self.sports_name = (data[0]['sport_nice'])

        # debug helper code
        # print(self.teams)
        # print(self.betting_sites)
        # print(self.h2h_odds)

    def sort_max_h2h_odds(self, sites_best=[], sites_safety=[], exclude_sites=[]):
        """  sort to get max odds offered for each team for all events. """

        sites_best_use_all = False
        sites_safety_use_all = False

        if (len(sites_best) == 0):
            # no restrictions use all sites
            sites_best_use_all = True
        if (len(sites_safety) == 0):
            # no restrictions use all sites
            sites_safety_use_all = True

        # calculate max_h2h_odds
        for i, event in enumerate(self.teams):
            # for each event

            # init list of 2 dictonarys (1 for each team) that contains the max odds and the site for those odds
            self.max_h2h_odds.append(
                {self.teams[i][0]: [0, "no site"], self.teams[i][1]: [0, "no site"]})

            for j, team in enumerate(self.teams[i]):
                # for each team
                for k, site_odds in enumerate(self.h2h_odds[i]):
                    # manual check to ignore Unibet odds for NHL
                    if (self.sports_name == 'NHL') and (self.betting_sites[i][k] == 'Unibet'):
                        continue
                    # restrict to sites to use. defaults to all
                    if (sites_best_use_all or (self.betting_sites[i][k] in sites_best)) and not (self.betting_sites[i][k] in exclude_sites):
                        # for all odds find largest and save. Also check exclude list
                        if site_odds[j] > self.max_h2h_odds[i][team][0]:
                            self.max_h2h_odds[i][team] = [
                                site_odds[j], self.betting_sites[i][k]]

        # calculate max_safety_odds
        for i, event in enumerate(self.teams):
            # for each event

            # init list of 2 dictonarys (1 for each team) that contains the max odds and the site for those odds
            self.max_safety_odds.append(
                {self.teams[i][0]: [0, "no site"], self.teams[i][1]: [0, "no site"]})

            for j, team in enumerate(self.teams[i]):
                # for each team
                for k, site_odds in enumerate(self.h2h_odds[i]):
                    # restrict to sites to use. defaults to all
                    if sites_safety_use_all or (self.betting_sites[i][k] in sites_safety) and not (self.betting_sites[i][k] in exclude_sites):
                        # for all odds find largest and save
                        if site_odds[j] > self.max_safety_odds[i][team][0]:
                            self.max_safety_odds[i][team] = [
                                site_odds[j], self.betting_sites[i][k]]

        #print('Finished finding max odds')

    def generate_odds_total_value(self):
        # gen odds total "value". Value is a number used for betting on both out comes and getting same return on both. The higher the more to be made
        # formula is = team2_odds / (team1_odds + team2_odds) * team1_odds

        if len(self.max_h2h_odds) < 0:
            print("Must first sort max h2h odds")
            return

        for i, event_odds in enumerate(self.max_h2h_odds):

            if not (event_odds[self.teams[i][1]][0] == 0) and not (event_odds[self.teams[i][0]][0] == 0):
                value = event_odds[self.teams[i][1]][0] / (
                    event_odds[self.teams[i][0]][0] + event_odds[self.teams[i][1]][0]) * event_odds[self.teams[i][0]][0]
            else:
                # avoid division by zero and make value 0
                value = 0

            self.odds_total_value.append(value)

    def check_for_h2h_odds_win_lose_thresholds(self, win_threshold=2.0, safety_bet_threshold=999):
        """  Alert if there is an event where odds are found for teams of an event above the thresholds """

        if len(self.max_h2h_odds) < 0:
            print('Have not sorted max h2h odds yet')
            return

        if safety_bet_threshold == 999:
            # no value given. use win threshold for both
            safety_bet_threshold = win_threshold

        for i, event in enumerate(self.teams):
            # for each event check if max odds for both teams is above the threshold
            team_one_above = False
            team_two_above = False
            team_one_stake = ""
            team_two_stake = ""

            # logic to determine what odds too print as max based on allowed sites and thresholds
            if (self.max_h2h_odds[i][event[0]][0] > win_threshold) and (self.max_safety_odds[i][event[1]][0] > safety_bet_threshold):
                team_one_above = True
                team_one_stake = "win"
                team_two_above = True
                team_two_stake = "safety"

            if (not team_one_above) and (not team_two_above):
                # dont have to worry about which is better as didnt pass thresholds in other ordering
                if (self.max_h2h_odds[i][event[1]][0] > win_threshold) and (self.max_safety_odds[i][event[0]][0] > safety_bet_threshold):
                    team_one_above = True
                    team_one_stake = "safety"
                    team_two_above = True
                    team_two_stake = "win"
            elif (self.max_safety_odds[i][event[0]][0] > self.max_safety_odds[i][event[1]][0]):
                # assume odds above thresholds found to reach above elif statement. Check if a flip ups the safety odds
                if (self.max_h2h_odds[i][event[1]][0] > win_threshold) and (self.max_safety_odds[i][event[0]][0] > safety_bet_threshold):
                    team_one_above = True
                    team_one_stake = "safety"
                    team_two_above = True
                    team_two_stake = "win"

            if team_one_above and team_two_above:
                #print('Found Arbitrage opportunity for event ', i)
                temp_max_h2h_odds = []
                if (team_one_stake == "win") and (team_two_stake == "safety"):
                    temp_max_h2h_odds = {
                        event[0]: self.max_h2h_odds[i][event[0]], event[1]: self.max_safety_odds[i][event[1]]}
                elif (team_one_stake == "safety") and (team_two_stake == "win"):
                    temp_max_h2h_odds = {
                        event[0]: self.max_safety_odds[i][event[0]], event[1]: self.max_h2h_odds[i][event[1]]}

                self.bet_opportunities['odds data'].append(temp_max_h2h_odds)
                self.bet_opportunities['match index'].append(i)
                self.bet_opportunities['start time'].append(
                    self.start_time['string format'][i])
                self.bet_opportunities['time till start'].append(
                    self.start_time['time till start'][i])
                # odds total value overriden from max to max odds value generated earlier
                odds_value = self.calc_odds_value(temp_max_h2h_odds)
                self.bet_opportunities['odds total value'].append(
                    odds_value)
                self.odds_total_value[i] = odds_value
                if odds_value > self.bet_opportunities['max value']:
                    self.bet_opportunities['max value'] = odds_value

    def check_for_h2h_odds_total_value(self, value_threshold=2.0):
        """  Alert if there is an event where odds total value above threshold """

        if len(self.max_h2h_odds) < 0:
            print('Have not sorted max h2h odds yet')
            return

        for i, event in enumerate(self.teams):
            # for each event check if total odds value is above the threshold
            if self.odds_total_value[i] > value_threshold:
                #print('Found Arbitrage opportunity for event ', i)
                self.bet_opportunities['odds data'].append(
                    self.max_h2h_odds[i])
                self.bet_opportunities['match index'].append(i)
                self.bet_opportunities['start time'].append(
                    self.start_time['string format'][i])
                self.bet_opportunities['time till start'].append(
                    self.start_time['time till start'][i])
                self.bet_opportunities['odds total value'].append(
                    self.odds_total_value[i])

                if self.odds_total_value[i] > self.bet_opportunities['max value']:
                    self.bet_opportunities['max value'] = self.odds_total_value[i]
    
    def calc_odds_value(self, odds):
        # calculate odds vale for given 2 odds in dictionary
        keys = odds.keys()
        odds_values = list(odds.values())
        if not (odds_values[0][0] == 0) and not (odds_values[1][0] == 0):
            value = odds_values[1][0] / (
                odds_values[0][0] + odds_values[1][0]) * odds_values[0][0]
        else:
            # avoid division by zero and make value 0
            value = 0

        return value



if __name__ == '__main__':
    main()
