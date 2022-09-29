import glob
import os
import re
import asyncio
import time

from util import starprint


# allow for testing, by forcing the bot to read an old log logfile
# TEST_ELF = False
TEST_ELF = True


class EverquestLogFile:
    """
    class to encapsulate Everquest log logfile operations.
    This class is intended as a base class for any
    child class that needs log parsing abilities.

    The custom log parsing logic in the child class is accomplished by
    overloading the process_line() method
    """

    def __init__(self, base_directory: str, logs_directory: str, heartbeat: int) -> None:
        """
        ctor

        Args:
            base_directory: Base installation directory for Everquest
            logs_directory: Logs directory, typically '\\logs\\'
            heartbeat: Number of seconds of logfile inactivity before a check is made to re-determine most recent logfile
        """
        # instance data
        self.base_directory = base_directory
        self.logs_directory = logs_directory
        self._char_name = 'Unknown'
        self.server_name = 'Unknown'
        self.logfile_name = 'Unknown'
        self.logfile = None

        # are we parsing
        self._parsing = False

        self.prevtime = time.time()
        self.heartbeat = heartbeat

    def set_char_name(self, name: str) -> None:
        """
        allow derived classes to override this as necessary, to do whatever is needed when tracking toon changes

        Args:
            name: player whose log file is being parsed
        """
        self._char_name = name

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

    def open_latest(self, seek_end=True) -> bool:
        """
        open the logfile with most recent mod time (i.e. latest).

        Args:
            seek_end: True if parsing is to begin at the end of the logfile, False if at the beginning

        Returns:
            object: True if a new logfile was opened, False otherwise
        """
        # get a list of all log files, and sort on mod time, latest at top
        mask = self.base_directory + self.logs_directory + 'eqlog_*_*' + '.txt'
        files = glob.glob(mask)
        files.sort(key=os.path.getmtime, reverse=True)

        # if no files are found to parse, bail out
        if len(files) == 0:
            starprint(f'ERROR: Unable to open any log files in directory [{self.base_directory}]')
            return False

        latest_file = files[0]

        # extract the character name from the logfile_name
        # note that windows pathnames must use double-backslashes in the pathname
        # note that backslashes in regular expressions are double-double-backslashes
        # this expression replaces double \\ with quadruple \\\\, as well as the logfile_name mask asterisk to a
        # named regular expression
        names_regexp = mask.replace('\\', '\\\\').replace('eqlog_*_*', 'eqlog_(?P<charname>[\\w ]+)_(?P<servername>[\\w]+)')
        m = re.match(names_regexp, latest_file)

        rv = False

        # figure out what to do
        # if we are already parsing a logfile, and it is the latest logfile - do nothing
        if self.is_parsing() and (self.logfile_name == latest_file):
            # do nothing
            pass

        # if we are already parsing a logfile, but it is not the latest logfile, close the old and open the latest
        elif self.is_parsing() and (self.logfile_name != latest_file):
            # stop parsing old and open the new logfile
            self.close()

            # self._char_name = m.group('charname')
            self.set_char_name(m.group('charname'))
            rv = self.open(latest_file, seek_end)

        # if we aren't parsing any logfile, then open latest
        elif not self.is_parsing():

            # self._char_name = m.group('charname')
            self.set_char_name(m.group('charname'))
            rv = self.open(latest_file, seek_end)

        return rv

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
            starprint('OS error: {0}'.format(err))
            starprint('Unable to open logfile_name: [{}]'.format(filename))
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
            starprint('Already parsing character log for: [{}]'.format(self._char_name))

        else:

            # use a back door to force the system to read a test logfile
            if TEST_ELF:

                # read a sample logfile for testing
                logfile_name = './data/test/test_input.txt'

                # start parsing, but in this case, start reading from the beginning of the logfile,
                # rather than the end (default)
                rv = self.open(logfile_name, seek_end=False)

            # open the latest logfile
            else:
                # open the latest logfile, and kick off the parsing process
                rv = self.open_latest()

            # if the log logfile was successfully opened, then initiate parsing
            if rv:
                # status message
                starprint('Now parsing character log for: [{}]'.format(self._char_name))

                # create the asyncio coroutine and kick it off
                asyncio.create_task(self.run())

            else:
                starprint('ERROR: Could not open character log logfile for: [{}]'.format(self._char_name))
                starprint('Log logfile_name: [{}]'.format(self.logfile_name))

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
            now = time.time()
            if line:
                self.prevtime = now

                # process this line
                await self.process_line(line)

            else:
                # check the heartbeat.  Has our logfile gone silent?
                elapsed_seconds = (now - self.prevtime)

                if elapsed_seconds > self.heartbeat:
                    starprint(f'[{self._char_name}] heartbeat over limit, elapsed seconds = {elapsed_seconds:.2f}')
                    self.prevtime = now

                    # attempt to open latest log logfile - returns True if a new logfile is opened
                    if self.open_latest():
                        starprint('Now parsing character log for: [{}]'.format(self._char_name))

                # if we didn't read a line, pause just for a 100 msec blink
                await asyncio.sleep(0.1)

        starprint(f'Stopped parsing character log for: [{self._char_name}]')

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

        # cut off the leading date-time stamp info
        # trunc_line = line[27:]


#
# test driver
#
async def main():

    base_directory = 'c:\\users\\ewjax\\Documents\\Gaming\\Everquest-Project1999'
    logs_directory = '\\logs\\'
    # server_name = 'P1999Green'
    heartbeat = 15

    elf = EverquestLogFile(base_directory, logs_directory, heartbeat)

    print('creating and starting elf, then sleeping for 20')
    elf.go()

    count = 20
    for n in range(count):
        print(f'------------------- tick {n} ---------------------')
        await asyncio.sleep(1)

    # test the ability to stop and restart the parsing
    print('stopping elf, then sleeping for 5')
    elf.stop_parsing()

    count = 5
    for n in range(count):
        print(f'------------------- tick {n} ---------------------')
        await asyncio.sleep(1)

    print('restarting elf, then sleeping for 30')
    elf.go()

    count = 30
    for n in range(count):
        print(f'------------------- tick {n} ---------------------')
        await asyncio.sleep(1)

    print('done done')
    elf.stop_parsing()


if __name__ == '__main__':
    asyncio.run(main())
