
MAXBUFFLENGTH = 1950


#
#
#
class SmartBuffer:
    """
    A class to help manage long streams of text being sent to Discord
    There is apparently a limit of 2000 characters on any message, anything over that throws an
    exception

    this class works by just creating a list of buffers, none of which is over the MAXBUFFLENGTH limit
    Note that when using this, it is important to access the list of buffers using the get_bufflist()
    method, to ensure any remaining content currently stored in the working_buffer is added to the list
    """

    # ctor
    def __init__(self):

        # create a list of strings, each less than MAXBUFFLENGTH in length
        self._bufflist = []
        self._working_buffer = ''

    def add(self, a_string: str) -> None:
        """
        Add the string 'a_string' to the SmartBuffer

        :param a_string: str
        """
        # would the new string make the buffer too long?
        if (len(self._working_buffer) + len(a_string)) > MAXBUFFLENGTH:
            self._bufflist.append(self._working_buffer)
            self._working_buffer = ''

        self._working_buffer += a_string

    def get_bufflist(self) -> list:
        """
        :return: list of strings, each less than MAXBUFFLENTH bytes in length
        """
        # add any content currently in the working buffer to the list
        if self._working_buffer != '':
            self._bufflist.append(self._working_buffer)

        # return the list of buffers
        return self._bufflist


# report width
REPORT_WIDTH = 100


# standalone function to print results to terminal window
def starprint(line: str, alignment: str = '<', fill: str = ' ') -> None:
    """
    utility function to print with leading and trailing ** indicators

    Args:
        line: line to be printed
        alignment: (left, centered, right) are denoted by one of (<, ^, >)
        fill: Character to fill with
    """
    width = REPORT_WIDTH
    print(f'** {line.rstrip():{fill}{alignment}{width}} **')
