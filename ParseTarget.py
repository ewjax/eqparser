import re
import time
from datetime import datetime, timezone, timedelta


#
#
class ParseTarget:
    """
    class that encapsulates all information about any particular event that is detected in a logfile
    """

    #
    #
    def __init__(self):
        """
        constructor
        """

        # todo - need setter functions for these two data items
        self.short_description = 'Vessel Drozlin spawn!'
        self._target = 'Vessel Drozlin'

        self._search_list = [
            f'^{self._target} begins to cast a spell',
            f'^{self._target} engages (?P<playername>[\\w ]+)!',
            f'^{self._target} has been slain',
            f'^{self._target} says',
            f'^You have been slain by {self._target}'
        ]

        # the actual line from the logfile
        self._matching_line = None

        # timezone info
        self._local_datetime = None
        self._utc_datetime = None

        # field separation character, used in the report() function
        self.field_separator = '|'

    #
    #
    def matches(self, line: str) -> bool:
        """
        Check to see if the passed line matches the search criteria for this ParseTarget

        Args:
            line: line of text from the logfile

        Returns:
            True/False

        """
        # return value
        rv = False

        # cut off the leading date-time stamp info
        trunc_line = line[27:]

        # walk through the target list and trigger list and see if we have any match
        for trigger in self._search_list:

            # return value m is either None of an object with information about the RE search
            m = re.match(trigger, trunc_line)
            if m:
                rv = True

                # save the matching line and set the timestamps
                self._matching_line = line
                self._set_timestamps(line)

        # return self.matched
        return rv

    def _set_timestamps(self, line: str) -> None:

        # creates a naive datetime, unaware of TZ, from the passed EQ timestamp string
        eq_timestamp = line[0:26]
        eq_datetime = datetime.strptime(eq_timestamp, '[%a %b %d %H:%M:%S %Y]')

        # convert it to an aware datetime, by adding the local tzinfo using replace()
        # time.timezone = offset of the local, non-DST timezone, in seconds west of UTC
        local_tz = timezone(timedelta(seconds=-(time.timezone)))
        self._local_datetime = eq_datetime.replace(tzinfo=local_tz)

        # now convert it to a UTC datetime
        self._utc_datetime = self._local_datetime.astimezone(timezone.utc)

        # print(f'{self._local_datetime}')
        # print(f'{self._utc_datetime}')


    #
    #
    def report(self) -> str:
        """
        Return a line of text with all relevant data for this event,
        separated by the field_separation character

        Returns:
            str: single line with all fields
        """
        rv = f'{self.short_description}{self.field_separator}'
        rv += f'{self._utc_datetime}{self.field_separator}'
        rv += f'{self._local_datetime}{self.field_separator}'
        rv += f'{self._matching_line}'
        return rv


def main():
    vd = ParseTarget()

    line_list = ['[Mon May 31 16:05:42 2021] Vessel Drozlin engages Azleep!',
                 '[Mon May 31 16:06:09 2021] Vessel Drozlin begins to cast a spell.',
                 "[Mon May 31 16:09:18 2021] Vessel Drozlin says, 'You may get the Rod of Xolion, but the Crusaders of Greenmist will bury you in this pit!'",
                 '[Mon May 31 16:09:18 2021] Vessel Drozlin has been slain by Crusader Golia!',
                 '[Mon May 31 16:09:18 2021] You have been slain by Vessel Drozlin!',
                 '[Mon May 31 16:09:18 2021] Something here that does not match'
                 ]

    for line in line_list:
        if vd.matches(line):
            print(vd.report())


if __name__ == '__main__':
    main()

#
# parse targets:
#
# VD
# VT
# Dain
# Sev
# CT
# Earthquake
# FTE
# Tangrin
# Yael
# server random
# you have been slain


# # list of targets which this log file watches for
# _search_list = [
#     'Verina Tomb',
#     'Vessel Drozlin',
#     'Dain Frostreaver IV',
#     'Severilous',
#     'tangrin',
#     'The Gods of Norrath',
#     'Master Yael'
# ]
#
# # list of regular expressions matching log files indicating the 'target' is spawned and active
# trigger_list = [
#     '^(?P<target>[\\w ]+)\'s body pulses with mystic fortitude',
#     '^(?P<target>[\\w ]+) is cloaked in a shimmer of glowing symbols',
#     '^(?P<target>[\\w ]+) begins to cast a spell',
#     '^(?P<target>[\\w ]+) engages (?P<playername>[\\w ]+)!',
#     '^(?P<target>[\\w ]+) has been slain',
#     '^(?P<target>[\\w ]+) says',
#     '^The (?P<target>[\\w ]+) (hits|tries to hit|bashes|tries to bash)',
#     '^You have been slain by the (?P<target>[\\w ]+)',
#     '^(?P<target>[\\w ]+) emit a sinister laugh as they toy with their creations'
# ]
