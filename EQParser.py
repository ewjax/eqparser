import asyncio
import pywin32_bootstrap
import win32console

import EverquestLogFile
import config
import _version

import util
from util import starprint
from ParseTarget import *


#################################################################################################


#
#
class EQParser(EverquestLogFile.EverquestLogFile):

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

        # # create a list of parsers
        # self.parse_target_list = [
        #     VesselDrozlin_Parser(),
        #     VerinaTomb_Parser(),
        #     DainFrostreaverIV_Parser(),
        #     Severilous_Parser(),
        #     CazicThule_Parser(),
        #     MasterYael_Parser(),
        #     FTE_Parser(),
        #     PlayerSlain_Parser(),
        #     Earthquake_Parser(),
        #     Random_Parser(),
        # ]

        # create a list of parsers
        self.parse_target_list = [
            CommsFilter_Parser(),
        ]


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
            starprint(f'EQParser {_version.__VERSION__}')

        # check for .help command
        target = r'^\.help'
        m = re.match(target, trunc_line)
        if m:
            EQParser.help_message()

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
                starprint(f'Parsing character log for:    [{self.char_name}]')
                starprint(f'Log filename:                 [{self.logfile_name}]')
                starprint(f'Heartbeat timeout (seconds):  [{self.heartbeat}]')
            else:
                starprint(f'Not currently parsing')

        # check current line for matches in any of the list of Parser objects
        for parse_target in self.parse_target_list:
            if parse_target.matches(line):
                report_str = parse_target.report()

                # todo - process the report information in some manner
                print(report_str, end='')


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
        starprint('EQParser:  Help', '^')
        starprint('')
        starprint('User commands are accomplished by sending a tell to the below fictitious player names:')
        starprint('')
        starprint('General')
        starprint('  .help          : This message')
        starprint('  .status        : Show logfile parsing status')
        starprint('  .save          : Force console window on screen position to be saved/remembered')
        starprint('  .ver           : Display EQParser current version')
        starprint('  .ini           : Display contents of EQParser.ini')
        starprint('')
        starprint('', '^', '*')
        starprint('')


#################################################################################################


async def main():
    # set console title
    win32console.SetConsoleTitle('EQParser')

    # print a startup message
    starprint('')
    starprint('=', alignment='^', fill='=')
    starprint(f'EQParser {_version.__VERSION__}', alignment='^')
    starprint('=', alignment='^', fill='=')
    starprint('')

    # create and start the EQParser parser
    config.the_parser = EQParser()
    config.the_parser.go()

    starprint('EQParser running')
    config.the_parser.help_message()

    # while True followed by pass seems to block asyncio coroutines, so give the asyncio task a chance to break out
    while True:
        # sleep for 100 msec
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(main())
