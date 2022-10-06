import os
import asyncio

import config
from util import starprint

# allow for testing, by forcing the bot to read an old log logfile
TEST_LF = False
#TEST_LF = True


class LogFile:
    """
    class to encapsulate general logfile "tail" operations.
    This class is intended as a base class for any
    child class that needs log parsing abilities.

    The custom log parsing logic in the child class is accomplished by
    overloading the process_line() method
    """

    def __init__(self) -> None:

        self._parsing = False
        self.logfile_name = 'Unknown'
        self.logfile = None

    def set_parsing(self) -> None:
        """
        called when parsing is active
        """
        self._parsing = True

    def clear_parsing(self) -> None:
        """
        called when parsing is no longer active
        """
        self._parsing = False

    def is_parsing(self) -> bool:
        """
        Returns:
            object: Is the logfile being actively parsed
        """
        return self._parsing

    def open(self, filename: str, seek_end=True) -> bool:
        """
        open the logfile.
        seek logfile position to end of logfile if passed parameter 'seek_end' is true

        Args:
            filename: full log logfile_name
            seek_end: True if parsing is to begin at the end of the logfile, False if at the beginning

        Returns:
            bool: True if a new logfile was opened, False otherwise
        """

        try:
            self.logfile = open(filename, 'r', errors='ignore')
            if seek_end:
                self.logfile.seek(0, os.SEEK_END)

            self.logfile_name = filename
            self.set_parsing()
            return True
        except OSError as err:
            starprint(f'OS error: {err}')
            starprint(f'Unable to open logfile name: [{filename}]')
            return False

    def close(self) -> None:
        """
        close the logfile
        """
        self.logfile.close()
        self.clear_parsing()

    def readline(self) -> str or None:
        """
        get the next line

        Returns:
            str or None: a string containing the next line, or None if no new lines to be read
        """
        if self.is_parsing():
            return self.logfile.readline()
        else:
            return None

    def go(self) -> bool:
        """
        call this method to kick off the parsing thread

        Returns:
            bool: True if logfile is opened successfully for parsing
        """
        rv = False

        # already parsing?
        if self.is_parsing():
            starprint('Already parsing logfile name: [{}]'.format(self.logfile_name))

        else:

            # use a back door to force the system to read a test logfile
            if TEST_LF:

                # read a sample logfile for testing
                logfile_name = './data/test/remote.log'

                # start parsing, but in this case, start reading from the beginning of the logfile,
                # rather than the end (default)
                rv = self.open(logfile_name, seek_end=False)

            # open the latest logfile
            else:
                # open the latest logfile, and kick off the parsing process
                logfile_name = config.config_data.get('rsyslog', 'file_name')
                rv = self.open(logfile_name)

            # if the log logfile was successfully opened, then initiate parsing
            if rv:
                # status message
                starprint(f'Now parsing logfile name: [{self.logfile_name}]')

                # create the asyncio coroutine and kick it off
                asyncio.create_task(self.run())

            else:
                starprint('ERROR: Could not open logfile name: [{}]'.format(self.logfile_name))

        return rv

    def stop_parsing(self) -> None:
        """
        call this function when ready to stop (opposite of go() function)
        """
        self.close()

    async def run(self) -> None:
        """
        this method will execute in its own asynco coroutine
        Note that it calls self.process_line() for each line, so child classes can overload that function
        to perform their particular parsing logic
        """

        # do this while the parsing flag is set, and exit if/when stop_parsing() is called
        while self.is_parsing():

            # read a line
            line = self.readline()
            if line:
                # process this line
                await self.process_line(line)

            else:
                # if we didn't read a line, pause just for a 100 msec blink
                await asyncio.sleep(0.1)

        starprint(f'Stopped parsing logfile name: [{self.logfile_name}]')

    async def process_line(self, line: str, printline: bool = False) -> None:
        """
        virtual method, to be overridden in derived classes to do whatever specialized
        parsing is required for that application.

        Args:
            line: line from logfile to be processed
            printline: boolean to indicate if the entire line should be echoed to the terminal window
        """

        if printline:
            print(line.rstrip())


async def main():
    logfile = LogFile()

    print('creating and starting logfile, then sleeping for 20')
    logfile.go()

    count = 20
    for n in range(count):
        print(f'------------------- tick {n} ---------------------')
        await asyncio.sleep(1)

    # test the ability to stop and restart the parsing
    print('stopping logfile, then sleeping for 5')
    logfile.stop_parsing()

    count = 5
    for n in range(count):
        print(f'------------------- tick {n} ---------------------')
        await asyncio.sleep(1)

    print('restarting logfile, then sleeping for 30')
    logfile.go()

    count = 30
    for n in range(count):
        print(f'------------------- tick {n} ---------------------')
        await asyncio.sleep(1)

    print('done done')
    logfile.stop_parsing()


if __name__ == '__main__':
    asyncio.run(main())
