import re
import time
from datetime import datetime, timezone, timedelta


#########################################################################################################################
#
# Base class
#
class ParseTarget:
    """
    Base class that encapsulates all information about any particular event that is detected in a logfile
    """

    #
    #
    def __init__(self):
        """
        constructor
        """

        # modify these as necessary in child classes
        self.short_description = 'Generic Target Name spawn!'
        self._search_list = [
            '^Generic Target Name begins to cast a spell',
            '^Generic Target Name engages (?P<playername>[\\w ]+)!',
            '^Generic Target Name has been slain',
            '^Generic Target Name says',
            '^You have been slain by Generic Target Name'
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

                # allow for any additional logic to be applied, if needed, by derived classes
                if self._additional_match_logic(m):
                    rv = True

                    # save the matching line and set the timestamps
                    self._set_timestamps(line)

        # return self.matched
        return rv

    # provide a hook for derived classes to override this method and specialize the search
    # default action is simply return true
    def _additional_match_logic(self, m: re.Match) -> bool:
        if m:
            return True

    def _set_timestamps(self, line: str) -> None:
        """
        Utility function to set the local and UTC timestamp information,
        using the EQ timestamp information present in the first 26 characters
        of every Everquest log file line

        Args:
            line: line from the logfile
        """

        # save the matching line
        self._matching_line = line

        # creates a naive datetime object, unaware of TZ, from the passed EQ timestamp string
        eq_timestamp = line[0:26]
        eq_datetime = datetime.strptime(eq_timestamp, '[%a %b %d %H:%M:%S %Y]')

        # convert it to an aware datetime, by adding the local tzinfo using replace()
        # time.timezone = offset of the local, non-DST timezone, in seconds west of UTC
        local_tz = timezone(timedelta(seconds=-time.timezone))
        self._local_datetime = eq_datetime.replace(tzinfo=local_tz)

        # now convert it to a UTC datetime
        self._utc_datetime = self._local_datetime.astimezone(timezone.utc)

        # print(f'{eq_datetime}')
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


#########################################################################################################################
#
# Derived classes
#

class VesselDrozlin_Parser(ParseTarget):
    """
    Parser for Vessel Drozlin spawn
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'Vessel Drozlin spawn!'
        self._search_list = [
            '^Vessel Drozlin begins to cast a spell',
            '^Vessel Drozlin engages (?P<playername>[\\w ]+)!',
            '^Vessel Drozlin has been slain',
            '^Vessel Drozlin says',
            '^You have been slain by Vessel Drozlin'
        ]


class VerinaTomb_Parser(ParseTarget):
    """
    Parser for Verina Tomb spawn
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'Verina Tomb spawn!'
        self._search_list = [
            '^Verina Tomb begins to cast a spell',
            '^Verina Tomb engages (?P<playername>[\\w ]+)!',
            '^Verina Tomb has been slain',
            '^Verina Tomb says',
            '^You have been slain by Verina Tomb'
        ]
        
        
class MasterYael_Parser(ParseTarget):
    """
    Parser for Master Yael spawn
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'Master Yael spawn!'
        self._search_list = [
            '^Master Yael begins to cast a spell',
            '^Master Yael engages (?P<playername>[\\w ]+)!',
            '^Master Yael has been slain',
            '^Master Yael says',
            '^You have been slain by Master Yael'
        ]


class DainFrostreaverIV_Parser(ParseTarget):
    """
    Parser for Dain Frostreaver IV spawn
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'Dain Frostreaver IV spawn!'
        self._search_list = [
            '^Dain Frostreaver IV engages (?P<playername>[\\w ]+)!',
            '^Dain Frostreaver IV says',
            '^Dain Frostreaver IV has been slain',
            '^You have been slain by Dain Frostreaver IV'
        ]


class Severilous_Parser(ParseTarget):
    """
    Parser for Severilous spawn
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'Severilous spawn!'
        self._search_list = [
            '^Severilous begins to cast a spell',
            '^Severilous engages (?P<playername>[\\w ]+)!',
            '^Severilous has been slain',
            '^Severilous says',
            '^You have been slain by Severilous'
        ]


class CazicThule_Parser(ParseTarget):
    """
    Parser for Cazic Thule spawn
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'Cazic Thule spawn!'
        self._search_list = [
            '^Cazic Thule engages (?P<playername>[\\w ]+)!',
            '^Cazic Thule has been slain',
            '^Cazic Thule says',
            '^You have been slain by Cazic Thule',
            "Cazic Thule  shouts 'Denizens of Fear, your master commands you to come forth to his aid!!"
        ]


class FTE_Parser(ParseTarget):
    """
    Parser for general FTE messages
    overrides _additional_match_logic() for additional info to be captured
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'FTE!'
        self._search_list = [
            '^(?P<target_name>[\\w ]+) engages (?P<playername>[\\w ]+)!'
        ]

    # overload the default base class behavior to add some additional logic
    def _additional_match_logic(self, m: re.Match) -> bool:
        if m:
            target_name = m.group('target_name')
            playername = m.group('playername')
            self.short_description = f'FTE: {target_name} engages {playername}'
            return True


class PlayerSlain_Parser(ParseTarget):
    """
    Parser for player has been slain
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'Player Slain!'
        self._search_list = [
            '^You have been slain by (?P<target_name>[\\w ]+)'
        ]


class Earthquake_Parser(ParseTarget):
    """
    Parser for Earthquake
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'Earthquake!'
        self._search_list = [
            '^The Gods of Norrath emit a sinister laugh as they toy with their creations'
        ]


class ServerRandom_Parser(ParseTarget):
    """
    Parser for Server Random (0-1000)
    Here we somewhat arbitrarily define a Server Random as any that are done 0-1000
    overrides _additional_match_logic() for additional info to be captured
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'Server Random!'
        self._search_list = [
            '^\\*\\*It could have been any number from 0 to 1000, but this time it turned up a (?P<value>[0-9]+)\\.'
        ]

    # overload the default base class behavior to add some additional logic
    def _additional_match_logic(self, m: re.Match) -> bool:
        if m:
            value = m.group('value')
            self.short_description = f'Server Random! Value={value}'
            return True


class GeneralRandom_Parser(ParseTarget):
    """
    Parser for General Random (low-high)
    overrides _additional_match_logic() for additional info to be captured
    """
    def __init__(self):
        super().__init__()
        self.short_description = 'General Random!'
        self._search_list = [
            '\\*\\*It could have been any number from (?P<low>[0-9]+) to (?P<high>[0-9]+), but this time it turned up a (?P<value>[0-9]+)\\.'
        ]

    # overload the default base class behavior to add some additional logic
    def _additional_match_logic(self, m: re.Match) -> bool:
        if m:
            low = m.group('low')
            high = m.group('high')
            value = m.group('value')
            self.short_description = f'Random roll: {low}-{high}, Value={value}'
            return True


def main():

    line_list = [
        '[Mon May 31 16:05:42 2021] Vessel Drozlin engages Azleep!',
        '[Mon May 31 16:06:09 2021] Vessel Drozlin begins to cast a spell.',
        "[Mon May 31 16:09:18 2021] Vessel Drozlin says, 'You may get the Rod of Xolion, but the Crusaders of Greenmist will bury you in this pit!'",
        '[Mon May 31 16:09:18 2021] Vessel Drozlin has been slain by Crusader Golia!',
        '[Mon May 31 16:09:18 2021] You have been slain by Vessel Drozlin!',
        '[Mon May 31 16:09:18 2021] Something here that does not match',
        '[Fri May 21 21:38:14 2021] Verina Tomb engages Erenion!',
        '[Fri May 21 21:38:45 2021] Verina Tomb begins to cast a spell.',
        "[Fri May 21 21:39:25 2021] Verina Tomb says 'You will not evade me Leffingwell!'",
        '[Fri May 21 21:40:49 2021] Verina Tomb has been slain by Venann!',
        '[Fri May 21 21:40:49 2021] Another misc line that does not match',
        '[Thu Aug 12 22:50:23 2021] Dain Frostreaver IV engages Nightadder!',
        "[Thu Aug 12 22:30:39 2021] Dain Frostreaver IV says 'Several of our greatest officers, including a few veterans from the War of Yesterwinter are assembling just outside our city. Gather your army at once and give this parchment and the ninth ring to Sentry Badian. I will remain inside the city with a few of my troops to defend it against any who might penetrate your defense. May Brell be with you, Raolador.'",
        "[Thu Aug 12 22:30:43 2021] Dain Frostreaver IV says 'The people of Thurgadin are in your debt, Meaners. Please accept the Coldain Hero's Ring as a token of our gratitude. The curse has been removed from the blade as well. I hope you find it useful against our common foes. When you are interested in assisting me further please show me the blade. Until that day, may Brell bless and protect you.'",
        "[Thu Aug 12 22:30:48 2021] Dain Frostreaver IV says 'The people of Thurgadin are in your debt, Gortex. Please accept the Coldain Hero's Ring as a token of our gratitude. The curse has been removed from the blade as well. I hope you find it useful against our common foes. When you are interested in assisting me further please show me the blade. Until that day, may Brell bless and protect you.'",
        "[Thu Aug 12 22:31:16 2021] Dain Frostreaver IV says, 'My good Azleep, you have served me well. You have flushed out all who sought to oppose me and my people. I am afraid I need to call upon you and your friends one final time. The dissension and treason ran deeper than I had anticipated. Our population has been cleansed, but we lost a full third of our army to the poisonous words of those rebels. In retaliation for your deeds, the Kromrif have made plans to attack us in this, our weakest hour. Can I count on your help outlander?'",
        '[Fri May 21 21:38:14 2021] Severilous engages Erenion!',
        '[Fri May 21 21:38:45 2021] Severilous begins to cast a spell.',
        "[Fri May 21 21:39:25 2021] Severilous says 'You will not evade me Leffingwell!'",
        '[Fri May 21 21:40:49 2021] Severilous has been slain by Venann!',
        "[Sat Aug 13 15:24:40 2022] Cazic Thule  shouts 'Denizens of Fear, your master commands you to come forth to his aid!!",
        '[Sat Feb 19 13:34:30 2022] The Gods of Norrath emit a sinister laugh as they toy with their creations. They are reanimating creatures to provide a greater challenge to the mortals',
        '[Sat Aug 14 17:04:32 2021] Master Yael begins to cast a spell.',
        "[Sat Aug 14 17:04:43 2021] Master Yael says 'DOOMSTRESS'",
        "[Sat Aug 14 17:07:18 2021] You have been slain by Master Yael!",
        '[Wed Sep 21 16:47:54 2022] **It could have been any number from 0 to 10000, but this time it turned up a 687.',
        '[Wed Sep 21 16:47:54 2022] **It could have been any number from 0 to 1000, but this time it turned up a 687.',
        '[Sun Sep 18 14:14:42 2022] **It could have been any number from 0 to 100, but this time it turned up a 94.',
        ]

    # create a list of parsers
    parse_target_list = [
        VesselDrozlin_Parser(),
        VerinaTomb_Parser(),
        DainFrostreaverIV_Parser(),
        Severilous_Parser(),
        CazicThule_Parser(),
        MasterYael_Parser(),
        FTE_Parser(),
        PlayerSlain_Parser(),
        Earthquake_Parser(),
        ServerRandom_Parser(),
        GeneralRandom_Parser(),
    ]

    # simulate a logfile list of lines
    for line in line_list:
        for parse_target in parse_target_list:
            if parse_target.matches(line):
                print(parse_target.report())


if __name__ == '__main__':
    main()
