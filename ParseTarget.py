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
                if self._custom_match_hook(m, line):
                    rv = True

                    # save the matching line and set the timestamps
                    self._set_timestamps(line)

        # return self.matched
        return rv

    #
    #
    def _custom_match_hook(self, m: re.Match, line: str) -> bool:
        """
        provide a hook for derived classes to override this method and specialize the search
        default action is simply return true

        Args:
            m: re.Match object from the search
            line: current line

        Returns:
            True/False if this is a match
        """
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
    def _custom_match_hook(self, m: re.Match, line: str) -> bool:
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


class Random_Parser(ParseTarget):
    """
    Parser for Random (low-high)
    overrides _additional_match_logic() for additional info to be captured
    """

    def __init__(self):
        super().__init__()
        self.playername = None
        self.short_description = 'Random!'
        self._search_list = [
            '\\*\\*A Magic Die is rolled by (?P<playername>[\\w ]+)\\.',
            '\\*\\*It could have been any number from (?P<low>[0-9]+) to (?P<high>[0-9]+), but this time it turned up a (?P<value>[0-9]+)\\.'
        ]

    # overload the default base class behavior to add some additional logic
    def _custom_match_hook(self, m: re.Match, line: str) -> bool:
        rv = False
        if m:
            # if m is true, and contains the playername group, this represents the first line of the random dice roll event
            # save the playername for later
            if 'playername' in m.groupdict().keys():
                self.playername = m.group('playername')
            # if m is true but doesn't have the playername group, then this represents the second line of the random dice roll event
            else:
                low = m.group('low')
                high = m.group('high')
                value = m.group('value')
                self.short_description = f'Random roll: {self.playername}, {low}-{high}, Value={value}'
                self.playername = None
                rv = True

        return rv


class CommsFilter_Parser(ParseTarget):
    """
    Parser for Comms Filter
    allows filtering on/off the various communications channels
    """

    def __init__(self):
        super().__init__()

        # individual exclude flags, just in case wish to customize this later for finer control, for whatever reason
        # without this level of complication, the final regex can be boiled down to
        #       '^(?![\\w ]+ (told|tell(s)?|say(s)?|auction(s)?|shout(s)?|-> [\\w ]+:))'
        # but we'll keep the complicated approach, just in case its needed down the road
        exclude_tell = True
        exclude_say = True
        exclude_group = True
        exclude_auc = True
        exclude_ooc = True
        exclude_shout = True
        exclude_guild = True

        # tells
        # [Sun Sep 18 15:22:41 2022] You told Snoiche, 'gotcha'
        # [Sun Sep 18 15:16:43 2022] Frostclaw tells you, 'vog plz'
        # [Thu Aug 18 14:31:34 2022] Azleep -> Berrma: have you applied?
        # [Thu Aug 18 14:31:48 2022] Berrma -> Azleep: ya just need someone to invite i believe
        tell_regex = ''
        if exclude_tell:
            tell_regex1 = "You told [\\w ]+, '"
            tell_regex2 = "[\\w ]+ tells you, '"
            tell_regex3 = "[\\w ]+ -> [\\w ]+:"
            tell_regex = f'^(?!{tell_regex1}|{tell_regex2}|{tell_regex3})'

        # say
        # [Sat Aug 13 15:36:21 2022] You say, 'lfg'
        # [Sun Sep 18 15:17:28 2022] Conceded says, 'where tf these enchs lets goo'
        say_regex = ''
        if exclude_say:
            say_regex1 = "You say, '"
            say_regex2 = "[\\w ]+ says, '"
            say_regex = f'^(?!{say_regex1}|{say_regex2})'

        # group
        # [Fri Aug 12 18:12:46 2022] You tell your party, 'Mezzed << froglok ilis knight >>'
        # [Fri Aug 12 18:07:08 2022] Mezmurr tells the group, 'a << myconid reaver >> is slowed'
        group_regex = ''
        if exclude_group:
            group_regex1 = "You tell your party, '"
            group_regex2 = "[\\w ]+ tells the group, '"
            group_regex = f'^(?!{group_regex1}|{group_regex2})'

        # auction
        # [Wed Jul 20 15:39:25 2022] You auction, 'wts Smoldering Brand // Crystal Lined Slippers // Jaded Electrum Bracelet // Titans Fist'
        # [Wed Sep 21 17:54:28 2022] Dedguy auctions, 'WTB Crushed Topaz'
        auc_regex = ''
        if exclude_auc:
            auc_regex1 = "You auction, '"
            auc_regex2 = "[\\w ]+ auctions, '"
            auc_regex = f'^(?!{auc_regex1}|{auc_regex2})'

        # ooc
        # [Sat Aug 20 22:19:09 2022] You say out of character, 'Sieved << a scareling >>'
        # [Sun Sep 18 15:25:39 2022] Piesy says out of character, 'Come port with the Puffbottom Express and <Dial a Port>! First-Class travel'
        ooc_regex = ''
        if exclude_ooc:
            ooc_regex1 = "You say out of character, '"
            ooc_regex2 = "[\\w ]+ says out of character, '"
            ooc_regex = f'^(?!{ooc_regex1}|{ooc_regex2})'

        # shout
        # [Fri Jun 04 16:16:41 2021] You shout, 'I'M SORRY WILSON!!!'
        # [Sun Sep 18 15:21:05 2022] Abukii shouts, 'ASSIST --       Cleric of Zek '
        shout_regex = ''
        if exclude_shout:
            shout_regex1 = "You shout, '"
            shout_regex2 = "[\\w ]+ shouts, '"
            shout_regex = f'^(?!{shout_regex1}|{shout_regex2})'

        # guild
        # [Fri Aug 12 22:15:07 2022] You say to your guild, 'who got fright'
        # [Fri Sep 23 14:18:03 2022] Kylarok tells the guild, 'whoever was holding the chain coif for Pocoyo can nvermind xD'
        guild_regex = ''
        if exclude_guild:
            guild_regex1 = "You say to your guild, '"
            guild_regex2 = "[\\w ]+ tells the guild, '"
            guild_regex = f'^(?!{guild_regex1}|{guild_regex2})'

        # put them all together
        self.short_description = 'Comms Filter'
        self._search_list = [
            f'{tell_regex}{say_regex}{group_regex}{auc_regex}{ooc_regex}{shout_regex}{guild_regex}',
        ]
