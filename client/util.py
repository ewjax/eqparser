from win32gui import FindWindow, GetWindowRect, MoveWindow


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


#
#
def get_window_coordinates() -> (int, int, int, int):
    """
    Get the windows rectangle of the console window

    Returns:
        Tuple of four integers representing the (x, y, width, height) dimensions
    """

    # return value
    rv = (0, 0, 0, 0)

    # use win32gui function
    window_handle = FindWindow(None, 'EQParser')
    if window_handle:
        # use win32gui function
        (upper_left_x, upper_left_y, lower_right_x, lower_right_y) = GetWindowRect(window_handle)
        x = upper_left_x
        y = upper_left_y
        width = lower_right_x - upper_left_x
        height = lower_right_y - upper_left_y
        rv = (x, y, width, height)

    return rv


#
#
def move_window(x: int, y: int, width: int, height: int) -> None:
    """
    Move the console window to the indicated screen location.
    The windows coordinate system has the origin in the upper left corner,
    with positive x dimenstions proceeding left to right, and positive
    y dimensions proceeding top to bottom

    Args:
        x: x position, pixels
        y: y position, pixels
        width: window width, pixels
        height: window height, pixels
    """

    # use win32gui function
    window_handle = FindWindow(None, 'EQParser')
    if window_handle:

        # use win32gui function
        MoveWindow(window_handle, x, y, width, height, True)
