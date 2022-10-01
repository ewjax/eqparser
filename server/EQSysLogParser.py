import asyncio
import re
from datetime import datetime

import _version
import LogFile
from util import starprint


#################################################################################################


#
#
class EQSysLogParser(LogFile.LogFile):

    def __init__(self) -> None:
        super().__init__()

        # parsing landmarks
        self.field_separator = '\\|'
        self.eqmarker = 'EQ__'

    #
    # process each line
    async def process_line(self, line: str, printline: bool = False) -> None:
        # call parent to edit every line, the default behavior
        await super().process_line(line, printline)

        # does this line contain a EQ report?
        target = f'^.*{self.eqmarker}{self.field_separator}'
        target += f'(?P<charname>.+){self.field_separator}'
        target += f'(?P<parse_target_ID>.+){self.field_separator}'
        target += f'(?P<short_desc>.+){self.field_separator}'
        target += f'(?P<utc_timestamp_str>.+){self.field_separator}'
        target += f'(?P<eq_log_line>.+)'
        m = re.match(target, line)
        if m:
            # print(line, end='')
            charname = m.group('charname')
            parse_target_ID = m.group('parse_target_ID')
            short_desc = m.group('short_desc')
            eq_log_line = m.group('eq_log_line')

            # convert the timestamp string into a datetime object, for use in reporting or de-duping of other reports
            utc_timestamp_datetime = datetime.fromisoformat(m.group('utc_timestamp_str'))

            # todo - do something useful with the received data
            print(f'{charname} --- {parse_target_ID} --- {short_desc} --- {utc_timestamp_datetime} --- {eq_log_line}')


#################################################################################################


async def main():
    # print a startup message
    starprint('')
    starprint('=', alignment='^', fill='=')
    starprint(f'EQSysLogParser {_version.__VERSION__}', alignment='^')
    starprint('=', alignment='^', fill='=')
    starprint('')

    # create and start the EQParser parser
    the_parser = EQSysLogParser()
    the_parser.go()

    starprint('EQSysLogParser running')

    # while True followed by pass seems to block asyncio coroutines, so give the asyncio task a chance to break out
    while True:
        # sleep for 100 msec
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(main())
