# FAA-registry-checker
Checks the FAA Registry daily for new aircraft registered by configured owner names, and optionally posts alerts to a Discord channel via webhook.

Currently only searches for new aircraft by owner/registry name but plan to add more features like deregister, detect update to registration, and N-Number reserve.

## Requirements
- Python 3.9+
- pip packages: `colorama`, `pytz`, `discord-webhook`, `pause`, `requests`

Install dependencies:
```
pip install -r requirements.txt
```

## Setup

### 1. Configure `./configs/mainconf.ini`

**[TIME]**  
Set your timezone for console display using tz database names (e.g. `America/New_York`). Full list [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). Defaults to UTC if invalid.

**[SEARCH]**  
`NAMES` — JSON array of owner names to watch, exactly as they appear in the FAA registry (all caps). Example:
```
NAMES = ["DELTA AIR LINES INC", "AMERICAN AIRLINES INC"]
```
To find the exact name format, look up an aircraft on the [FAA Registry](https://registry.faa.gov/aircraftinquiry/Search/NNumberResult) and use the registrant name as shown.

**[DISCORD]**  
Set `ENABLE = True` and provide your webhook `URL` to receive Discord alerts for new registrations. Leave `ENABLE = False` to use terminal output only.

### 2. Run
```
python __main__.py
```

The program will automatically download the FAA registry database on first run and re-download it each cycle. It checks once daily at 05:00 UTC.

## Example output
```
-------- 0 -------- 11:00:41 PM --------------------------------------------------------------------
Already have FAA_Reg_DB_Latest.zip deleting and redownloading
Successfully got FAA_Reg_DB_Latest.zip
1851 Current Regs in searched names
-------- 1 -------- 11:00:41 PM ------------------------Elapsed Time- 12.764 -----------------------
Sleeping till 2021-07-01 05:00:00+00:00
-------- 1 -------- 11:00:41 PM --------------------------------------------------------------------
Already have FAA_Reg_DB_Latest.zip deleting and redownloading
Successfully got FAA_Reg_DB_Latest.zip
Found new reg for BANK OF UTAH TRUSTEE N296NV a AIRBUS A320-214 https://registry.faa.gov/aircraftinquiry/Search/NNumberResult?NNumbertxt=296NV
Found new reg for BANK OF UTAH TRUSTEE N876GJ a BELL HELICOPTER TEXTRON CANADA 407 https://registry.faa.gov/aircraftinquiry/Search/NNumberResult?NNumbertxt=876GJ
Found new reg for BANK OF UTAH TRUSTEE N89NC a GULFSTREAM AEROSPACE CORP GVII-G600 https://registry.faa.gov/aircraftinquiry/Search/NNumberResult?NNumbertxt=89NC
1854 Current Regs in searched names
-------- 2 -------- 11:00:41 PM ------------------------Elapsed Time- 11.219 -----------------------
Sleeping till 2021-07-02 05:00:00+00:00
-------- 2 -------- 11:00:41 PM --------------------------------------------------------------------
Already have FAA_Reg_DB_Latest.zip deleting and redownloading
Successfully got FAA_Reg_DB_Latest.zip
Found new reg for BANK OF UTAH TRUSTEE N228JV a TEXTRON AVIATION INC 560XL https://registry.faa.gov/aircraftinquiry/Search/NNumberResult?NNumbertxt=228JV
Found new reg for BANK OF UTAH TRUSTEE N578GJ a BOMBARDIER INC CL-600-2C10 https://registry.faa.gov/aircraftinquiry/Search/NNumberResult?NNumbertxt=578GJ
1856 Current Regs in searched names
-------- 3 -------- 11:00:41 PM ------------------------Elapsed Time- 30.341 -----------------------
Sleeping till 2021-07-03 05:00:00+00:00
```
