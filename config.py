import configparser
from util import starprint

# global instance of the EQParser class
the_parser = None
ini_filename = 'EQParser.ini'


# global data
# begin by reading in the config data
config_data = configparser.ConfigParser()


def load() -> None:
    """
    Utility function to load contents from .ini logfile into a configparser.ConfigParser object
    """
    global config_data

    file_list = config_data.read(ini_filename)
    try:
        if len(file_list) == 0:
            raise ValueError(f'Unable to open ini logfile [{ini_filename}]')
    except ValueError as verr:
        starprint(f'{str(verr)}, creating default {ini_filename}')

    # confirm all needed sections and key values are present in the ini logfile
    verify_settings()

    # print out the contents
    show()


def verify_settings() -> None:
    """
    confirm all needed sections and key values are present in the ini logfile
    """
    global config_data
    modified = False

    # Everquest section
    section = 'Everquest'
    if not config_data.has_section(section):
        config_data.add_section(section)
        modified = True

    if not config_data.has_option(section, 'base_directory'):
        config_data.set(section, 'base_directory', 'c:\\everquest')
        modified = True

    if not config_data.has_option(section, 'logs_directory'):
        config_data.set(section, 'logs_directory', '\\logs\\')
        modified = True

    if not config_data.has_option(section, 'heartbeat'):
        config_data.set(section, 'heartbeat', '15')
        modified = True

    # screen positions section
    section = 'ConsoleWindowPosition'
    if not config_data.has_section(section):
        config_data.add_section(section)
        modified = True

    if not config_data.has_option(section, 'x'):
        config_data.set(section, 'x', '100')
        modified = True

    if not config_data.has_option(section, 'y'):
        config_data.set(section, 'y', '100')
        modified = True

    if not config_data.has_option(section, 'width'):
        config_data.set(section, 'width', '1200')
        modified = True

    if not config_data.has_option(section, 'height'):
        config_data.set(section, 'height', '800')
        modified = True

    # save the data
    if modified:
        save()
        show()


def save() -> None:
    """
    Utility function to save contents to .ini logfile from the configparser.ConfigParser object
    """
    global config_data
    with open(ini_filename, 'wt') as inifile:
        config_data.write(inifile)

    # # print out the contents
    # show()


def show() -> None:
    """
    print out the contents
    """
    global config_data

    starprint(f'{ini_filename} contents:', alignment='^', fill='-')
    for section in config_data.sections():
        starprint(f'[{section}]')
        for key in config_data[section]:
            val = config_data[section][key]
            starprint(f'    {key} = {val}')
    starprint(f'.', alignment='^', fill='.')
