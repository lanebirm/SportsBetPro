# python version 3.8.0
# Author: Lane Birmingham

import pytz
from datetime import datetime


def main():
    print('Shouldnt print this statement. File for import only')


class TimeConvertor():
    def __init__(self):
        super().__init__()
        self.fmt = '%d-%m-%Y %H:%M:%S %Z%z'
        self.tz = pytz.timezone('Australia/Brisbane')
        self.local_time = ""
        self.local_time_string = ""
        self.time_until = ""
        #print('Timezone init to ', self.tz)

    def convert_to_AEST(self, timestamp):
        """ Convert unix timestamp to Aus eastern standard time """

        utc_time = pytz.utc.localize(datetime.utcfromtimestamp(timestamp))
        # print(utc_time.strftime(self.fmt))

        as_timezone = utc_time.astimezone(self.tz)
        # print(as_timezone.strftime(self.fmt))

        self.local_time = self.tz.normalize(as_timezone)
        self.local_time_string = self.local_time.strftime(self.fmt)
        time_now = datetime.now(self.tz)
        self.time_until = self.local_time - time_now
        # print('test')


if __name__ == '__main__':
    main()
