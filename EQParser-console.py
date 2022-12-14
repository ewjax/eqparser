import asyncio
import re
from datetime import datetime

import _version
import config
import LogFile
from util import starprint


#################################################################################################

# all different


#
#
class EQParser(LogFile.LogFile):

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


#################################################################################################


async def main():
    # print a startup message
    starprint('')
    starprint('=', alignment='^', fill='=')
    starprint(f'EQParser {_version.__VERSION__}', alignment='^')
    starprint('=', alignment='^', fill='=')
    starprint('')

    # create and start the EQParser parser
    the_parser = EQParser()
    the_parser.go()

    starprint('EQParser running')

    # while True followed by pass seems to block asyncio coroutines, so give the asyncio task a chance to break out
    while True:
        # sleep for 100 msec
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(main())
