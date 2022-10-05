

import asyncio
import re
from datetime import datetime
import discord
from discord.ext import commands

import _version
import config
import LogFile
from util import starprint




#################################################################################################

#
#
class EQSysLogParser(LogFile.LogFile):

    def __init__(self) -> None:
        super().__init__()

        # force global data to load from ini logfile
        config.load()

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
            log_event_id = m.group('log_event_id')
            short_desc = m.group('short_desc')
            eq_log_line = m.group('eq_log_line')

            # convert the timestamp string into a datetime object, for use in reporting or de-duping of other reports
            utc_timestamp_datetime = datetime.fromisoformat(m.group('utc_timestamp_str'))

            # todo - do something useful with the received data, e.g. put all spawn messages in this channel, 
            # put all TOD messages in that channel, use the UTC timestamp to de-dupe, etc
            print(f'{charname} --- {log_event_id} --- {short_desc} --- {utc_timestamp_datetime} --- {eq_log_line}')

            if self.ctx:
                await self.ctx.send(f'{charname} --- {log_event_id} --- {short_desc} --- {utc_timestamp_datetime}')

            await client.alarm(msg=f'{charname} --- {log_event_id} --- {short_desc} --- {utc_timestamp_datetime} --- {eq_log_line}')


the_parser = EQSysLogParser()
the_parser.go()

starprint('EQSysLogParser running')


#################################################################################################


#################################################################################################

# # add intents
# my_intents = discord.Intents.default()
# my_intents.message_content = True


# define the client instance to interact with the discord bot
class myClient(commands.Bot):

    #
    # ctor
    def __init__(self, my_prefix):
        super().__init__(command_prefix=my_prefix)

    # sound the alarm
    async def alarm(self, msg):

        # try to find the #pop channels
        # if ctx.guild.name == myconfig.PERSONAL_SERVER_NAME:
        #     pop_channel = client.get_channel(myconfig.PERSONAL_SERVER_POPID)
        #     await pop_channel.send(msg)
        #
        # elif ctx.guild.name == myconfig.SNEK_SERVER_NAME:
        #     pop_channel = client.get_channel(myconfig.SNEK_SERVER_POPID)
        #     await pop_channel.send(msg)
        #
        # # if we didn't find the #pop channel for whatever reason, just bang it to current channel
        # else:
        #     await ctx.send(msg)

        channel = client.get_channel(879070487790120982)
        await channel.send(msg)


# create the global instance of the client that manages communication to the discord bot
prefix = config.config_data.get('Discord', 'bot_command_prefix')
client = myClient(prefix)


#################################################################################################

#
# add decorator event handlers to the client instance
#

# on_ready
@client.event
async def on_ready():
    print('Spawn Tracker 2000 is alive!')
    print('Discord.py version: {}'.format(discord.__version__))

    print('Logged on as {}!'.format(client.user))
    print('App ID: {}'.format(client.user.id))


# on_message - catches everything, messages and commands
# note the final line, which ensures any command gets processed as a command, and not just absorbed here as a message
@client.event
async def on_message(message):
    author = message.author
    content = message.content
    channel = message.channel
    print('Content received: [{}] from [{}] in channel [{}]'.format(content, author, channel))
    await client.process_commands(message)


# ping command
@client.command()
async def ping(ctx):
    print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))
    await ctx.send('Latency = {} ms'.format(round(client.latency * 1000)))


# start command
@client.command()
async def go(ctx):
    print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))
    the_parser.go(ctx)


# status command
@client.command()
async def status(ctx):
    print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))

    # if elf.is_parsing():
    #     await ctx.send('Parsing character log for: [{}]'.format(elf.char_name))
    #     await ctx.send('Log filename: [{}]'.format(elf.filename))
    #     await ctx.send('Parsing initiated by: [{}]'.format(elf.author))
    #     await ctx.send('Heartbeat timeout (minutes): [{}]'.format(elf.heartbeat))
    #
    # else:
    #     await ctx.send('Not currently parsing')


#################################################################################################


def main():
    # print a startup message
    starprint('')
    starprint('=', alignment='^', fill='=')
    starprint(f'EQSysLogParser {_version.__VERSION__}', alignment='^')
    starprint('=', alignment='^', fill='=')
    starprint('')

    # create and start the EQParser parser

    # let's go!!  this command is blocking
    token = config.config_data.get('Discord', 'bot_token')
    client.run(token)

if __name__ == '__main__':
    main()
