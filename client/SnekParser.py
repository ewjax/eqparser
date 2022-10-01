import asyncio
import pywin32_bootstrap
import win32console
import logging
import logging.handlers


import EverquestLogFile
import config
import _version

import util
from util import starprint
from ParseTarget import *

# list of rsyslog (host, port) information
remote_list = [
    ('192.168.1.127', 514),
    ('ec2-3-133-158-247.us-east-2.compute.amazonaws.com', 22514),
]


#################################################################################################


#
#
class SnekParser(EverquestLogFile.EverquestLogFile):

    def __init__(self) -> None:

        # force global data to load from ini logfile
        config.load()

        # move console window to saved position
        x = config.config_data.getint('ConsoleWindowPosition', 'x')
        y = config.config_data.getint('ConsoleWindowPosition', 'y')
        width = config.config_data.getint('ConsoleWindowPosition', 'width')
        height = config.config_data.getint('ConsoleWindowPosition', 'height')
        util.move_window(x, y, width, height)

        # parent ctor
        base_dir = config.config_data.get('Everquest', 'base_directory')
        logs_dir = config.config_data.get('Everquest', 'logs_directory')
        heartbeat = config.config_data.getint('Everquest', 'heartbeat')
        super().__init__(base_dir, logs_dir, heartbeat)

        # create a list of parsers
        self.parse_target_list = [
            VesselDrozlin_Parser(),
            VerinaTomb_Parser(),
        ]

        # set up a custom logger to use for rsyslog comms
        self.logger_list = []

        logging.basicConfig(level=logging.INFO)

        for (host, port) in remote_list:
            eq_logger = logging.getLogger(f'{host}:{port}')
            log_handler = logging.handlers.SysLogHandler(address=(host, port))
            eq_logger.addHandler(log_handler)
            self.logger_list.append(eq_logger)

    def set_char_name(self, name: str) -> None:
        """
        override base class setter function to also sweep thru list of parse targets 
        and set their parsing player names

        Args:
            name: player whose log file is being parsed
        """
        super().set_char_name(name)
        for parse_target in self.parse_target_list:
            parse_target.parsing_player = name

    #
    # process each line
    async def process_line(self, line: str, printline: bool = False) -> None:
        # call parent to edit every line, the default behavior
        await super().process_line(line, printline)

        # cut off the leading date-time stamp info
        trunc_line = line[27:]

        # save console window positioning
        target = r'^\.save '
        m = re.match(target, trunc_line)
        if m:
            (x, y, width, height) = util.get_window_coordinates()

            section = 'ConsoleWindowPosition'
            config.config_data[section]['x'] = f'{x}'
            config.config_data[section]['y'] = f'{y}'
            config.config_data[section]['width'] = f'{width}'
            config.config_data[section]['height'] = f'{height}'

            # save the updated ini logfile
            config.save()
            starprint(f'Console window position saved to .ini file')

        # show current version number
        target = r'^\.ver '
        m = re.match(target, trunc_line)
        if m:
            starprint(f'SnekParser {_version.__VERSION__}')

        # check for .help command
        target = r'^\.help'
        m = re.match(target, trunc_line)
        if m:
            SnekParser.help_message()

        # check for .ini command
        target = r'^\.ini'
        m = re.match(target, trunc_line)
        if m:
            # show the ini file
            config.show()

        # check for .status command
        target = r'^\.status'
        m = re.match(target, trunc_line)
        if m:
            if self.is_parsing():
                starprint(f'Parsing character log for:    [{self._char_name}]')
                starprint(f'Log filename:                 [{self.logfile_name}]')
                starprint(f'Heartbeat timeout (seconds):  [{self.heartbeat}]')
            else:
                starprint(f'Not currently parsing')

        # check current line for matches in any of the list of Parser objects
        # if we find a match, then send the event report to the remote aggregator
        for parse_target in self.parse_target_list:
            if parse_target.matches(line):
                report_str = parse_target.report()
                # print(report_str, end='')

                # send the info to the remote log aggregator
                for logger in self.logger_list:
                    logger.info(report_str)

    #
    #
    @staticmethod
    def help_message() -> None:
        """
        Print out a Help message
        """
        starprint('')
        starprint('', '^', '*')
        starprint('')
        starprint('SnekParser:  Help', '^')
        starprint('')
        for (host, port) in remote_list:
            starprint(f'Sending parsing event reports to: {host}:{port}')
        starprint('')
        starprint('User commands are accomplished by sending a tell to the below fictitious player names:')
        starprint('')
        starprint('General')
        starprint('  .help          : This message')
        starprint('  .status        : Show logfile parsing status')
        starprint('  .save          : Force console window on screen position to be saved/remembered')
        starprint('  .ver           : Display SnekParser current version')
        starprint('  .ini           : Display contents of SnekParser.ini')
        starprint('')
        starprint('', '^', '*')
        starprint('')


#################################################################################################


async def main():
    # set console title
    win32console.SetConsoleTitle('SnekParser')

    # print a startup message
    starprint('')
    starprint('=', alignment='^', fill='=')
    starprint(f'SnekParser {_version.__VERSION__}', alignment='^')
    starprint('=', alignment='^', fill='=')
    starprint('')

    # create and start the SnekParser parser
    config.the_parser = SnekParser()
    config.the_parser.go()

    starprint('SnekParser running')
    config.the_parser.help_message()

    # while True followed by pass seems to block asyncio coroutines, so give the asyncio task a chance to break out
    while True:
        # sleep for 100 msec
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(main())
