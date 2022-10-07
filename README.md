# eqparser
General purpose parser engine for Everquest log files server, to receive reports from various parsing clients, all sending info to the server using the rsyslog service, using UDP packets.

To run this code:
```
python EQParser.py
```
---
#### *Client-Server Communication*
   
  - On python client:  done via the SysLogHandler built into the logging standard library
  - Uses the UDP interface (rather than TCP), so there is no reply acknowledgement required, the client can "fire and forget"
    - Advantage: speed (no wait for TCP reply)
    - Disadvantage: no confirmation to the client that the messages are being received by the server
  - On the server side
    - the unix rsyslog setup does not typically listen for TCP or UDP packets by default, that will need to be enabled and the service restarted
    - the default port is 514, but can be configured to something else if desired
    - the firewall will likely need that port opened for incoming traffic
    - the default filename to receive the rsyslog messages depends on the flavor of unix being used (usually /var/log/something), but can also be configured 
  - The client can send information to more than one rsyslog server, by adding hostname/IP address and port number to the following list of (host, port) tuples.  This example is sending the logging information to both a raspberry pi on my home network, as well as an Amazon Web Service EC2 virtual machine: 

```
# list of rsyslog (host, port) information
remote_list = [
    ('192.168.1.127', 514),
    ('ec2-3-133-158-247.us-east-2.compute.amazonaws.com', 22514),
]
```
---
#### *Report Format*
The concept is that each match generates a single line report that contains the relevant information for this event, with fields separated by LogEvent.field_separator character (default = '|').

Fields included in the rsyslog report:
1. A standard marker, default 'EQ__', to assist in downstream parsing
2. Player name
3. An integer ID, unique to that particular type of LogEvent,  to assist in downstream sorting and processing
4. Short description
5. UTC timestamp
6. The raw line from the everquest log file

Examples:
```
EQ__|Azleep|1|Vessel Drozlin spawn!|2021-05-31 23:05:42+00:00|[Mon May 31 16:05:42 2021] Vessel Drozlin engages Azleep!
EQ__|Azleep|7|FTE: Vessel Drozlin engages Azleep|2021-05-31 23:05:42+00:00|[Mon May 31 16:05:42 2021] Vessel Drozlin engages Azleep!
EQ__|Azleep|13|TOD (Slain Message): Vessel Drozlin|2021-05-31 23:09:18+00:00|[Mon May 31 16:09:18 2021] Vessel Drozlin has been slain by Crusader Golia!
EQ__|Azleep|12|Gratss|2022-09-18 23:41:50+00:00|[Sun Sep 18 16:41:50 2022] Snoiche tells the guild, 'Crexxus Crown of Narandi  500 Gratss me'
EQ__|Azleep|13|TOD|2021-07-03 08:19:27+00:00|[Sat Jul 03 01:19:27 2021] Jherin tells the guild, 'ToD Harla Dar'
EQ__|Azleep|14|GMOTD|2021-03-20 02:16:48+00:00|[Fri Mar 19 19:16:48 2021] GUILD MOTD: Zalkestna - - What do you call an elf who won't share? -----Elfish----That's your Friday GMOTD!  Have fun and be kind to one another!
```
---

The server should be able to listen / tail the appropriate rsyslog file, and decode it using something like:
```
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
            log_event_id = int(m.group('log_event_id'))
            short_desc = m.group('short_desc')
            eq_log_line = m.group('eq_log_line')

            # convert the timestamp string into a datetime object, for use in reporting or de-duping of other reports
            utc_timestamp_datetime = datetime.fromisoformat(m.group('utc_timestamp_str'))

            # do something useful with the collected data
            # print(f'{charname} --- {log_event_id} --- {short_desc} --- {utc_timestamp_datetime} --- {eq_log_line}')


```
The log_event_id field is a unique integer that conveys the even type.  Valid codes are as shown:

```
# define some ID constants for the derived classes
LOGEVENT_BASE: int = 0
LOGEVENT_VD: int = 1
LOGEVENT_VT: int = 2
LOGEVENT_YAEL: int = 3
LOGEVENT_DAIN: int = 4
LOGEVENT_SEV: int = 5
LOGEVENT_CT: int = 6
LOGEVENT_FTE: int = 7
LOGEVENT_PLAYERSLAIN: int = 8
LOGEVENT_QUAKE: int = 9
LOGEVENT_RANDOM: int = 10
LOGEVENT_ABC: int = 11
LOGEVENT_GRATSS: int = 12
LOGEVENT_TOD: int = 13
LOGEVENT_GMOTD: int = 14
```

---
