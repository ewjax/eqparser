# eqparser
General purpose parser engine for Everquest log files

To run this code:
```
python EQParser.py
```
---
### *ParseTarget base class concepts*

The meat of this content is found in the file ParseTarget.py, where several classes are defined:
  - ParseTarget, the base class
  - several classes which derive from ParseTarget, each designed to search for one particular event or occurrence
  
The fundamental design is for a standard Everquest log parser to read in each line from the log, and then walk the list of ParseTarget objects, calling the ParseTarget.matches(line) function on each, and if a match is found, to create a one-line report for each using the ParseTarget.report() function:
```
        # check current line for matches in any of the list of Parser objects
        for parse_target in self.parse_target_list:
            if parse_target.matches(line):
                report_str = parse_target.report()
                
                # process the match in some manner
                print(report_str, end='')
```               

### *ParseTarget.matches()*

Walks the list of regular expression trigger strings contained in ParseTarget._search_list, checking each for a match.  If a match is discovered, it then calls ParseTarget._custom_match_hook() for any additional processing which may be needed for that parse target.

The intention is that child class constructor funcitons will set customized _search_list regular expressions for that particular parse target.
Example base class ParseTarget._search_list:
```
        self.short_description = 'Generic Target Name spawn!'
        self._search_list = [
            '^Generic Target Name begins to cast a spell',
            '^Generic Target Name engages (?P<playername>[\\w ]+)!',
            '^Generic Target Name has been slain',
            '^Generic Target Name says',
            '^You have been slain by Generic Target Name'
        ]
```
Example child class _search_list intended to watch for Vessel Drozlin spawn:
```
        self.short_description = 'Vessel Drozlin spawn!'
        self._search_list = [
            '^Vessel Drozlin begins to cast a spell',
            '^Vessel Drozlin engages (?P<playername>[\\w ]+)!',
            '^Vessel Drozlin has been slain',
            '^Vessel Drozlin says',
            '^You have been slain by Vessel Drozlin'
        ]
```
Example child class _search_list intended to watch for FTE messages:
```
        self.short_description = 'FTE!'
        self._search_list = [
            '^(?P<target_name>[\\w ]+) engages (?P<playername>[\\w ]+)!'
        ]
```

### *ParseTarget._custom_match_hook()*
Once ParseTarget.matches() finds a match when checking against the _search_list of regular expression triggers, it then calls ParseTarget._custom_march_hook() method.  The default behavior is simply to return True, but the intention is to allow child classes to override this function to provide any additional logic.

Examples of possible uses of this function can be seen in the child classes 'FTE_Parser' and 'Random_Parser'.  In particular, FTE_Parser uses this function to capture the player name and target name in the short_description variable, and the Random_Parser class uses this function to add the logic necessary to deal with the fact that Everquest random events actually generate two lines in the log file, rather than one.
```
        self._search_list = [
            '\\*\\*A Magic Die is rolled by (?P<playername>[\\w ]+)\\.',
            '\\*\\*It could have been any number from (?P<low>[0-9]+) to (?P<high>[0-9]+), but this time it turned up a (?P<value>[0-9]+)\\.'
        ]
...
    # overload the default base class behavior to add some additional logic
    def _custom_match_hook(self, m: re.Match, line: str) -> bool:
        rv = False
        if m:
            # if m is true, and contains the playername group, this represents the first line of the random dice roll event
            # save the playername for later
            if 'playername' in m.groupdict().keys():
                self.playername = m.group('playername')
            # if m is true but doesn't have the playername group, then this represents the second line of the random dice roll event
            else:
                low = m.group('low')
                high = m.group('high')
                value = m.group('value')
                self.short_description = f'Random roll: {self.playername}, {low}-{high}, Value={value}'
                self.playername = None
                rv = True

        return rv

```

### *ParseTarget.report()*
The concept is that each match generates a single line report that contains the relevant information for this event, with fields separated by ParseTarget.field_separator character (default = '|').

Fields included in the report:
1. Short description
2. UTC timestamp
3. Local timestamp
4. The matching line

Examples:
```
Vessel Drozlin spawn!|2021-05-31 23:05:42+00:00|2021-05-31 16:05:42-07:00|[Mon May 31 16:05:42 2021] Vessel Drozlin engages Azleep!
FTE: Vessel Drozlin engages Azleep|2021-05-31 23:05:42+00:00|2021-05-31 16:05:42-07:00|[Mon May 31 16:05:42 2021] Vessel Drozlin engages Azleep!
Player Slain!|2021-08-15 00:07:18+00:00|2021-08-14 17:07:18-07:00|[Sat Aug 14 17:07:18 2021] You have been slain by Master Yael!
```
---
## *ParseTarget child classes*

Several child classes are pre-defined in ParseTarget.py, but the opportunity to create additional classes for other desired parsing targets is limited only by the imagination / need.

  - VesselDrozlin_Parser
  - VerinaTomb_Parser
  - MasterYael_Parser
  - DainFrostReaverIV_Parser
  - Severilous_Parser
  - CazicThule_Parser
  - FTE_Parser
  - PlayerSlain_Parser
  - Earthquake_Parser
  - Random_Parser

---
## Other Source Code 

- EQParser.py: Defines EQParser class, which derives from EverquestLogFile base class.  The construction function creates a list of ParseTarget child class objects to use for parsing individual logfile lines.  
```
        self.parse_target_list = [
            VesselDrozlin_Parser(),
            VerinaTomb_Parser(),
            DainFrostreaverIV_Parser(),
            Severilous_Parser(),
            CazicThule_Parser(),
            MasterYael_Parser(),
            FTE_Parser(),
            PlayerSlain_Parser(),
            Earthquake_Parser(),
            Random_Parser(),
        ]
```
  Overrides EverquestLogFile.process_line() function to walk its list of ParseTarget objects, checking for matches, and simply printing the reports to screen when matches are found
```
        # check current line for matches in any of the list of Parser objects
        for parse_target in self.parse_target_list:
            if parse_target.matches(line):
                report_str = parse_target.report()

                # todo - process the report information in some manner
                print(report_str, end='')

```
- EverquestLogfile.py:  Defines EverquestLogFile class, a general purpose class for use in managing/parsing Everquest log files.  Provides process_line() function which is intended to be overridden by child classes to perform whatever customized parsing is needed.  Default behavior is to open/parse the most-recent log file in the Everquest logs directory, but also provides ability to parse particular test input files by setting/clearing the TEST_ELF variable.
- config.py:  Primarily manages the interface to the associated .ini file
- util.py:  Utility functions
  
