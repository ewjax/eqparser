import re


#
# class that encapsulates all information about any particular event that is detected in a logfile
#
class ParseTarget:

    def __init__(self):
        """
        constructor
        """

        # todo - need setter functions for these two data items
        self._target = 'Vessel Drozlin'
        self._search_list = [
            '^(?P<target>[\\w ]+) begins to cast a spell',
            '^(?P<target>[\\w ]+) engages (?P<playername>[\\w ]+)!',
            '^(?P<target>[\\w ]+) has been slain',
            '^(?P<target>[\\w ]+) says',
            '^You have been slain by (?P<target>[\\w ]+)'
        ]

        # description
        # todo - setter?
        self.short_title = 'Vessel Drozlin spawn!'

        # the actual line from the logfile
        self._matching_line = 'tbd'

        # timestamp information for this event
        self._local_time_zone = 'tbd'
        self._local_time_stamp = 'TBD'
        self._eastern_time_stamp = 'TBD'

        # field separation character, used in the report() function
        self._field_separator = '|'

    def matches(self, line: str) -> bool:

        rv = False

        # cut off the leading date-time stamp info
        trunc_line = line[27:]

        # walk through the target list and trigger list and see if we have any match
        for trigger in self._search_list:

            # return value m is either None of an object with information about the RE search
            m = re.match(trigger, trunc_line)
            if m and (m.group('target') == self._target):
                rv = True

                # todo - set other parameters

        return rv

    def report(self) -> str:
        """
        Return a line of text with all relevant data for this event,
        separated by the field_separation character

        Returns:
            str: single line with all fields
        """
        return 'field separated report'


def main():
    vd = ParseTarget()

    line_list = ['[Mon May 31 16:05:42 2021] Vessel Drozlin engages Azleep!',
                 '[Mon May 31 16:06:09 2021] Vessel Drozlin begins to cast a spell.',
                 "[Mon May 31 16:09:18 2021] Vessel Drozlin says, 'You may get the Rod of Xolion, but the Crusaders of Greenmist will bury you in this pit!'",
                 '[Mon May 31 16:09:18 2021] Vessel Drozlin has been slain by Crusader Golia!',
                 '[Mon May 31 16:09:18 2021] Something here that does not match'
                 ]

    for line in line_list:
        print(f'{line}')
        if vd.matches(line):
            print('match')


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
