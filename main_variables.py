# python version 3.8.0

# TODO: Make a config file to load values from instead of hard codding


class MainVariables():
    """ class for all varibles of the main that have hardcoded defaults """

    def __init__(self, check_type=0):
        # init defaults
        # print('MainVariables init')
        # flags
        self.pull_api_data = True	 # pull data. if False reload data of last pull
        self.email_notify = True       # flag to push notify to phone
        self.print_data_frames = False   # Flag to print data with data frame tables
        # email notify list
        self.email_list = ['lanebirmbetnotify@gmail.com']
        # min value of the bet oppertunities max_value to prompt emailing notification
        self.email_notify_threshold = 0.9
        self.h2h_win_odds_threshold = 1.0  # top odds threshold
        self.h2h_safety_odds_threshold = 1.0  # safety odds threshold
        self.total_value_threshold = 0.5  # Total value threshold
        self.region_code = 'au'
        self.sports_names = ['americanfootball_ncaaf', 'americanfootball_nfl',
                             'aussierules_afl', 'esports_lol', 'mma_mixed_martial_arts', 'rugbyleague_nrl']
        self.sports_names_not_to_pull = ['icehockey_nhl', 'soccer_australia_aleague', 'soccer_denmark_superliga', 'soccer_efl_champ', 'soccer_england_league1', 'soccer_epl', 'soccer_fa_cup', 'soccer_finland_veikkausliiga', 'soccer_italy_serie_a', 'soccer_italy_serie_b', 'soccer_japan_j_league', 'soccer_korea_kleague1',
                                         'soccer_norway_eliteserien', 'soccer_portugal_primeira_liga', 'soccer_russia_premier_league', 'soccer_spain_la_liga', 'soccer_spain_segunda_division', 'soccer_sweden_allsvenskan', 'soccer_sweden_superettan', 'soccer_switzerland_superleague', 'soccer_turkey_super_league', 'soccer_uefa_europa_league', 'soccer_usa_mls', 'soccer_uefa_champs_league']
        self.sports_ignoring_keywords = ['soccer']

        self.odds_jsons = []
        self.data_processor = []
        # exclusion list for sports that "max value" is used to trigger emails
        self.sports_name_exclusion = []

        if check_type == 0:
            self.total_value_check()
        elif check_type == 1:
            self.win_lose_threshold()

    def total_value_check(self):
        # sites exclude list
        self.exclude_sites = []
        # sites to use. Empty means use all avalible
        self.sites_best = []
        self.sites_safety = []

    def win_lose_threshold(self):
        # sites exclude list
        self.exclude_sites = ['TAB']
        # sites to use. Empty means use all avalible
        self.sites_best = [] #['PointsBet (AU)']
        self.sites_safety = [] #['Bet Easy']


def main():
    # should not actually be run from here. import to different script
    print('main_variables should not be run directly')


if __name__ == '__main__':
    main()
