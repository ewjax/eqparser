# eqparser
General purpose parser engine for Everquest log files

The meat of this content is found in the file ParseTarget.py, where several classes are defined:
  - ParseTarget, the base class
  - several classes which derive from ParseTarget, each designed to search for one particular event or occurrence
  
The fundamental design is for a standard Everquest log parser to read in each line from the log, and then walk the list of ParseTarget objects, calling the ParseTarget.matches() function on each.



