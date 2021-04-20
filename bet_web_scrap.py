#!/usr/bin/env python3
# Author: Lane Birmingham

# Import required packages
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import pickle
import time

""" Structure example 
- Dictionary of data frames for each sport returned
- Keys match the OddsAPI data keys
- Have multiple links for each sport 

- Example return data_frame:

  site_nice	last_update	 odds.h2h	sport_nice	commence_time	teams	teams_string
0	Unibet	1575692772	[3.25, 1.34]	MMA	1575760500	[Martin Day, Virna Jandiroba]	Martin Day Virna Jandiroba
1	SportsBet	1575692780	[1.98, 1.83]	MMA	1575763200	[Bryce Mitchell, Matt Sayles]	Bryce Mitchell Matt Sayles


"""

FIREFOX_PAGE_LOAD_TIME = 2.0  # [secs]
SETTLE_TIME = 0.5  # [secs]


def main():
    # shouldnt run this
    print("Main. Should be running this file directly")


class WebScrapper():
    def __init__(self) -> None:
        self.search_list = [{"site_nice": "BetDeluxe",
                             "url": "https://www.betdeluxe.com.au/sports/basketball/nba-regular-season-1023233",
                             "sport_nice": "NBA"},
                             {"site_nice": "BetDeluxe",
                             "url": "https://www.betdeluxe.com.au/sports/baseball/major-league-baseball-regular-season-1029809",
                             "sport_nice": "MLB"},
                             {"site_nice": "Test"}]

        self.output_df_columns_ordering = ["site_nice", "last_update", "odds.h2h",
                                           "odds.h2h_lay", "sport_nice", "commence_time", "teams", "teams_string"]
        self.reset_result_df()
        self.current_search_list_index = None

        self.file_load_debug_mode = False

        if not self.file_load_debug_mode:
            options = webdriver.FirefoxOptions()
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--incognito')
            options.add_argument('--headless')
            self.selenium_driver = webdriver.Firefox(options=options)

    def reset_result_df(self):
        self.result_df = pd.DataFrame(columns=self.output_df_columns_ordering)

    def scrap_all_links(self):
        """ scraps all links in self.search_list """
        # dynamically call scraping
        for i, search in enumerate(self.search_list):
            self.current_search_list_index = i
            method_name = "scrap_" + search["site_nice"].lower()
            try:
                scrap_method = getattr(self, method_name)
            except:
                print("Method " + method_name + " does not exist. Skipping")
                continue
            success = scrap_method()

    def scrap_betdeluxe(self):
        """ scraps betdeluxe page for data """
        print("Called scrap_betdeluxe")

        # Load soup
        if self.file_load_debug_mode:
            soup = self.get_local_file_bs()  # TODO: load local version for testing
        else:
            soup = self.get_site_bs_with_selenium(
                self.search_list[self.current_search_list_index]["url"])

        # process soup
        identifiers = {}
        identifiers["team"] = [
            {"tag": "span", "class": "e1r8wjx61 css-66dkeu-Text-Text-SelectionItem-SelectionItem__Name-SelectionItem e10fjgi70"}]
        identifiers["single_odds"] = [{"tag": "div", "class": "css-sqcxnh-BettingAdd-styled-BettingAdd-BettingAdd-styled euibyvm3"},
                                      {"tag": "span", "class": "euibyvm1 css-11vfg1g-Text-Text-BettingAdd-styled-BettingAdd__Single-BettingAdd-styled e10fjgi70"}]

        scraped_data_dictonary = {}
        empty_list = []

        for key in identifiers.keys():
            # setup result
            scraped_data_dictonary[key] = empty_list.copy()
            # handle first identifier
            data_for_key = soup.find_all(
                identifiers[key][0]["tag"], class_=identifiers[key][0]["class"])
            # handle any further keys
            for i, identifier in enumerate(identifiers[key]):
                if i == 0:
                    continue  # already handled
                for j, data in enumerate(data_for_key):
                    data_for_key[j] = data_for_key[j].find_all(
                        identifier["tag"], class_=identifier["class"])
            for element in data_for_key:
                if isinstance(element, list):
                    if len(element) > 1:
                        print("Multiple elements still found after using identifiers '" +
                              key + "' for scrap_betdeluxe")
                    else:
                        element = element[0]
                element = element.text.replace(u' \xa0', u'')
                scraped_data_dictonary[key].append(
                    element)  # save to data dict

        # now post process into dataframe format
        df_dict = {}
        df_dict['teams'] = []
        df_dict['teams_string'] = []
        df_dict['odds.h2h'] = []
        for i in range(0, len(scraped_data_dictonary['team']), 2):
            temp_dict = {scraped_data_dictonary['team'][i]:float(scraped_data_dictonary['single_odds'][i]) , scraped_data_dictonary['team'][i+1]:float(
                scraped_data_dictonary['single_odds'][i+1])}
            sorted_keys = sorted(temp_dict.keys())

            df_dict['teams'].append([sorted_keys[0], sorted_keys[1]])
            df_dict['teams_string'].append(sorted_keys[0]  + " " + sorted_keys[1])
            
            df_dict['odds.h2h'].append([temp_dict[sorted_keys[0]], temp_dict[sorted_keys[1]]])

        df = pd.DataFrame.from_dict(df_dict)

        # fill constant columns
        df['odds.h2h_lay'] = None
        df['last_update'] = None
        df['commence_time'] = 0  # TODO
        df['site_nice'] = self.search_list[self.current_search_list_index]['site_nice']
        df['sport_nice'] = self.search_list[self.current_search_list_index]['sport_nice']
        df = df[self.output_df_columns_ordering]  # reorder columns

        self.result_df = self.result_df.append(df, ignore_index=True)

        return True

    def scrap_test(self):
        """ scraps test page for data """
        print("Called scrap_test")
        return True

    def get_site_bs_with_requests(self, url):
        """ Get html with requests. Scrap url to soup """
        if url == "":
            print("no url given")
            return False

        headers_test = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'upgrade-insecure-requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
                        }

        response = requests.get(url, headers=headers_test)
        if response.status_code == 200:
            with open("last_scrap.html", 'wb') as f:
                f.write(response.content)
        else:
            print("did not recieve success status code. Statuss code is: " +
                  str(response.status_code))

        soup = BeautifulSoup(response.content, "html.parser")
        return soup

    def get_site_bs_with_selenium(self, url, load_confirm_xpath=None):
        """ Get html with selenium. Scrap url to soup """
        self.selenium_driver.get(url)
        page_loaded = False

        if load_confirm_xpath != None:
            # confirm load via xpath
            while not page_loaded:
                # check for elements
                odds_spans = self.selenium_driver.find_elements_by_xpath(
                    load_confirm_xpath)
                if len(odds_spans) > 0:
                    page_loaded = True
        else:
            # just wait for page to load. No confirmation
            time.sleep(FIREFOX_PAGE_LOAD_TIME)

        # let page settle. May not be needed
        time.sleep(SETTLE_TIME)

        with open("last_scrap.html", 'wb') as f:
            f.write(str.encode(self.selenium_driver.page_source))
        soup = BeautifulSoup(self.selenium_driver.page_source, 'lxml')
        return soup

    def get_local_file_bs(self):
        """ load html from a file. Used for testing to prevent spamming site """
        soup = BeautifulSoup(open("last_scrap.html", 'rb'), "html.parser")
        return soup


if __name__ == '__main__':
    # main()
    WS = WebScrapper()
    WS.scrap_all_links()

    print(WS.result_df)
