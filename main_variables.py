# python version 3.8.0

#TODO: Make a config file to load values from instead of hard codding

class MainVariables():
    """ class for all varibles of the main that have hardcoded defaults """

    def __init__(self):
        # init defaults
        #print('MainVariables init')
        # flags
        self.pull_api_data = True	 # pull data. if False reload data of last pull
        self.email_notify = False       # flag to push notify to phone
        # min value of the bet oppertunities max_value to prompt emailing notification
        self.email_notify_threshold = 1
        self.h2h_win_odds_threshold = 2.0  # top odds threshold
        self.h2h_safety_odds_threshold = 1.4  # safety odds threshold
        self.total_value_threshold = 0.985  # Total value threshold
        self.region_code = 'au'

        self.odds_jsons = []
        self.data_processor = []
        # sites exclude list
        self.exclude_sites = []
        # sites to use. Empty means use all avalible
        self.sites_best = []
        self.sites_safety = []
        # exclusion list for sports that "max value" is used to trigger emails
        self.sports_name_exclusion = []

def main():
    # should not actually be run from here. import to different script
    print('loaded pull_data')

if __name__ == '__main__':
    main()
    