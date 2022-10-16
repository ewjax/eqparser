

import asyncio
import socket
import re
from datetime import datetime, timedelta
import discord
from discord.ext import commands

import _version
import config
import LogFile
from util import starprint
from util import SmartBuffer


# define some ID constants for the derived classes
LOGEVENT_BASE: int = 0
LOGEVENT_VD: int = 1
LOGEVENT_VT: int = 2
LOGEVENT_YAEL: int = 3
LOGEVENT_DAIN: int = 4
LOGEVENT_SEV: int = 5
LOGEVENT_CT: int = 6
LOGEVENT_FTE: int = 7
LOGEVENT_PLAYERSLAIN: int = 8
LOGEVENT_QUAKE: int = 9
LOGEVENT_RANDOM: int = 10
LOGEVENT_ABC: int = 11
LOGEVENT_GRATSS: int = 12
LOGEVENT_TODLO: int = 13
LOGEVENT_GMOTD: int = 14
LOGEVENT_TODHI: int = 15


#################################################################################################

#
#
class EQParser(LogFile.LogFile):

    def __init__(self) -> None:
        super().__init__()

        # force global data to load from ini logfile
        config.load()

        # various channel id's from personal discord server
        self.personal_general = config.config_data.getint('Personal Discord Server', 'general')
        self.personal_pop = config.config_data.getint('Personal Discord Server', 'pop')
        self.personal_spawn = config.config_data.getint('Personal Discord Server', 'spawn')
        self.personal_alert = config.config_data.getint('Personal Discord Server', 'alert')
        self.personal_tod = config.config_data.getint('Personal Discord Server', 'tod')
        self.personal_gmotd = config.config_data.getint('Personal Discord Server', 'gmotd')

        # pop channel for snek discord server
        self.snek_pop = config.config_data.getint('Snek Discord Server', 'pop')

    #
    # process each line
    async def process_line(self, line: str, printline: bool = False) -> None:
        # call parent to edit every line, the default behavior
        await super().process_line(line, printline)

        # parsing landmarks
        field_separator = '\\|'
        eqmarker = 'EQ__'

        # does this line contain a EQ report?
        target = f'^.*{eqmarker}{field_separator}'
        target += f'(?P<charname>.+){field_separator}'
        target += f'(?P<log_event_id>.+){field_separator}'
        target += f'(?P<short_desc>.+){field_separator}'
        target += f'(?P<utc_timestamp_str>.+){field_separator}'
        target += f'(?P<eq_log_line>.+)'
        m = re.match(target, line)
        if m:
            # print(line, end='')
            charname = m.group('charname')
            log_event_id = int(m.group('log_event_id'))
            short_desc = m.group('short_desc')
            eq_log_line = m.group('eq_log_line')

            # convert the timestamp string into a datetime object, for use in reporting or de-duping of other reports
            utc_timestamp_datetime = datetime.fromisoformat(m.group('utc_timestamp_str'))

            # do something useful with the collected data
            # print(f'{charname} --- {log_event_id} --- {short_desc} --- {utc_timestamp_datetime} --- {eq_log_line}')


            # dispatch the parsed log events to the appropriate channels
            if log_event_id == LOGEVENT_VD or log_event_id == LOGEVENT_VT:
                await client.channel_report(self.personal_spawn, charname, log_event_id, short_desc, utc_timestamp_datetime, eq_log_line)
                await client.channel_report(self.personal_pop, charname, log_event_id, short_desc, utc_timestamp_datetime, eq_log_line, everyone=True)
                await client.channel_report(self.snek_pop, charname, log_event_id, short_desc, utc_timestamp_datetime, eq_log_line, everyone=True)

            elif log_event_id == LOGEVENT_YAEL or log_event_id == LOGEVENT_DAIN or log_event_id == LOGEVENT_SEV or log_event_id == LOGEVENT_CT:
                await client.channel_report(self.personal_spawn, charname, log_event_id, short_desc, utc_timestamp_datetime, eq_log_line)

            elif log_event_id == LOGEVENT_FTE or log_event_id == LOGEVENT_QUAKE or log_event_id == LOGEVENT_RANDOM or log_event_id == LOGEVENT_GRATSS:
                await client.channel_report(self.personal_alert, charname, log_event_id, short_desc, utc_timestamp_datetime, eq_log_line)

            elif log_event_id == LOGEVENT_TODLO or log_event_id == LOGEVENT_TODHI:
                await client.channel_report(self.personal_tod, charname, log_event_id, short_desc, utc_timestamp_datetime, eq_log_line)

            elif log_event_id == LOGEVENT_GMOTD:
                await client.channel_report(self.personal_gmotd, charname, log_event_id, short_desc, utc_timestamp_datetime, eq_log_line)

            else:
                await client.channel_report(self.personal_general, charname, log_event_id, short_desc, utc_timestamp_datetime, eq_log_line)


# create the global instance of the parser class
the_parser = EQParser()


#################################################################################################


#################################################################################################

# # add intents
# my_intents = discord.Intents.default()
# my_intents.message_content = True


# define the client instance to interact with the discord bot
class DiscordClient(commands.Bot):

    #
    # ctor
    def __init__(self, my_prefix):
        super().__init__(command_prefix=my_prefix)

    #
    # send output to indicated channel number
    async def channel_report(self, channel_id: int,
                             charname: str,
                             log_event_id: int,
                             short_desc: str,
                             utc_timestamp_datetime: datetime,
                             eq_log_line: str,
                             everyone: bool = False) -> None:
        """
        Issue a report to the indicated channel

        TODO:  Add de-duplicating functionality.  It seems reasonable that de-duplication might
        depend on the event type (log_event_ID), and make use of the UTC timestamp to establish
        a 'blackout window' that would preclude other events judged to be duplicates from being posted

        Args:
            channel_id: discord channel ID
            charname: character name of the toon who sent the report
            log_event_id: log event type number
            short_desc: short description
            utc_timestamp_datetime: UTC timestamp
            eq_log_line: raw line of text
            everyone: boolean flag, if True, prepend the message with '@everyone'
        """
        channel = client.get_channel(channel_id)
        if channel:

            hostname = socket.gethostname().lower()
            if hostname == 'fourbee':
                suffix = '[4]'
            else:
                suffix = '[v]'

            # accumulate all discord output into a SmartBuffer
            sb = SmartBuffer()

            if everyone:
                short_desc = '@everyone' + short_desc

            # send the first line of the report
            # await channel.send(f'{short_desc} (from: {charname})')
            sb.add(f'{short_desc} (from: {charname}) {suffix}')

            # convert the UTC to EDT (4 hours behind UTC), then represent it in the same format of an EQ timestamp
            edt_modifier = timedelta(hours=-4)
            edt_timestamp_datetime = utc_timestamp_datetime + edt_modifier
            edt_eqtimestamp_str = edt_timestamp_datetime.strftime('[%a %b %d %H:%M:%S %Y]')

            # send the second and third line of the report
            line = '```'
            line += f'Raw: {eq_log_line}'
            line += '\n'
            line += f'EDT: {edt_eqtimestamp_str}'
            line += '```'
            # await channel.send(line)
            sb.add(line)

            # send info from SmartBuffer to discord
            buff_list = sb.get_bufflist()
            for b in buff_list:
                await channel.send(b)


# create the global instance of the client that manages communication to the discord bot
prefix = config.config_data.get('Discord Bot', 'bot_command_prefix')
client = DiscordClient(prefix)


#################################################################################################

#
# add decorator event handlers to the client instance
#

# on_ready
@client.event
async def on_ready():
    starprint('Spawn Tracker 2000 is alive!')
    starprint(f'Discord.py version: {discord.__version__}')
    starprint(f'Logged on as {client.user}')
    starprint(f'App ID: {client.user.id}')
    the_parser.go()


# on_message - catches everything, messages and commands
# note the final line, which ensures any command gets processed as a command, and not just absorbed here as a message
@client.event
async def on_message(message):
    author = message.author
    content = message.content
    channel = message.channel
    starprint(f'Content received: [{content}] from [{author}] in channel [{channel}]')
    await client.process_commands(message)


# ping command
@client.command()
async def ping(ctx):
    starprint(f'Command received: [{ctx.message.content}] from [{ctx.message.author}]')
    await ctx.send(f'Latency = {round(client.latency * 1000)} ms')


# status command
@client.command()
async def status(ctx):
    starprint(f'Command received: [{ctx.message.content}] from [{ctx.message.author}]')

    await ctx.send(f'EQParser {_version.__VERSION__}')

    if the_parser.is_parsing():
        await ctx.send(f'Now parsing logfile name: [{the_parser.logfile_name}]')
    else:
        await ctx.send('Not currently parsing')


#################################################################################################


def main():
    # print a startup message
    starprint('')
    starprint('=', alignment='^', fill='=')
    starprint(f'EQParser {_version.__VERSION__}', alignment='^')
    starprint('=', alignment='^', fill='=')
    starprint('')

    # let's go!!  this command is blocking
    token = config.config_data.get('Discord Bot', 'bot_token')
    client.run(token)


if __name__ == '__main__':
    main()
