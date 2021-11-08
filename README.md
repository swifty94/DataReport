# DataReport
Collecting TR-069 related data into reports


Application collecting TR-069 related data from FTL ACS database engine (MySQL) > Store it in lightweight SQLite DB > Providing several types of CSV reports with CPE related data
---

Installation:
---
    ``` git clone git@github.com:swifty94/DataReport.git ```  
    ``` pip3 install requirements.txt ```      
    ``` If no Internet - bash install.sh ```
Usage:
---    
1. To process CPE data from FTL DB and save to internal app DB use:

``` user@host:~$ python3 app.py collect ```

This will collect CPE related information to the internal lightweight SQLite3 database so it can be processed much faster for the reports after.

2. If data is collected already, you can process reports. Use:

``` user@host:~$ python3 app.py report fiber ```

``` Available options: full, fiber, guest_acc ```

3. Obtain a list of CPEs based on the WAN username list. Use:

``` user@host:~$ python3 app.py eat wan_usernames.txt ```

NOTE: 
You can also add '&' sing at the end of each app command (collect, report, eat) so it will be running in the background regardless of your presence on the server. 

On Windows: 
start /B python app.py $command

Once the command is issued you might track its progress in the app.log file. Use:

``` tail -f app.log ```  

to view how it is progressing while processing your request 

