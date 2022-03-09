# Create Users from CSV file

## Imports
* requests
* xml.etree.ElementTree
* csv
* argparse
* sys
* getpass
* os.path


## Includes

* class QualysUser
* class QualysAPI

## Usage
```
usage: create_users_from_csv.py [-h] [-c CONFIG] [-f FILENAME] [-e] [-u USERNAME] [-p PASSWORD] [-P] [-U PROXY_URL] [-a APIURL] [-n] [-d] [-x]

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file name (default: config.ini)
  -f FILENAME, --filename FILENAME
                        Input CSV file containing user information
  -e, --no_send_email   Do Not Send Email for user registration
  -u USERNAME, --username USERNAME
                        Qualys Username
  -p PASSWORD, --password PASSWORD
                        Qualys Password (use - for interactive input
  -P, --proxy_enable    Enable HTTPS proxy
  -U PROXY_URL, --proxy_url PROXY_URL
                        HTTPS proxy address
  -a APIURL, --apiurl APIURL
                        Qualys API URL (e.g. https://qualysapi.qualys.com)
  -n, --no_call         Do not make API calls, write URLs to console
  -d, --debug           Provide debugging output from API calls
  -x, --exit_on_error   Exit on error
                                                                                             
```

## Example
inputfile.csv
```csv
1, Joan, Redfern, joan.redfern@farringham.school, Nurse, 1234, Farringham Road, United Kingdom, SICKBAY, foo, OK
2, Timothy, Latimer, timothy.latimer@farringham.school, Student, 1234, Farringham Road, United Kingdom, BEER, foo, OK
3, Jeremy, Baines, jeremy.baines@farringham.school, Son, 1234, Farringham Road, United Kingdom, FAMILY;SON, foo, OK
4, Mister, Clark, mister.clark@oakham.farm, Father, 1234, Oakham Farm, United Kingdom, FAMILY;FATHER, foo, INCOMPLETE
5, Mister, Rocastle, headmaster@farringham.school, Headmaster, 1234, Farringham Road, United Kingdom, SCHOOL, NOT_OK
```
<br>

```commandline
python -f inputfile.csv -e -u redfr-td -p - -P -U https://proxy.address -a https://qualysapi.qualys.eu
Enter password : 

User redfr-ar45 (Joan Redfern) Created
User redfr-tl4 (Timothy Latimer) Created
User redfr-eb45 (Jeremy Baines) Created
Skipping INCOMPLETE entry for Mister Clark
Skipping INCOMPLETE entry for Mister Rocastle
```

## Input files

Create Qualys user accounts from user information stored in a CSV file, in accordance with the rules set out in the
configuration file ('config.ini' by default)

### Configuration File
Example
```
[SKIP_RECORDS]
skip_records = TRUE
skip_record_indicator = INCOMPLETE,NOT_OK
skip_record_column = 11

[OVERRIDE]
city = London
time_zone_code = GB
business_unit = Unassigned

[COLUMNS]
forename = 1
surname = 2
email = 3
title = 4
phone = 5
address1 = 6
country = 8
asset_groups = 9
external_id = 3
```
The configuration file **must** include the sections [SKIP_RECORDS], [OVERRIDE] and [COLUMNS] and **must** include the
following fields in either the [OVERRIDE] or [COLUMNS] sections
* forename
* surname
* email
* title
* phone
* address1
* city
* country
* asset_groups
* time_zone_code
* external_id
* business_unit

If a field is specified in both [OVERRIDE] and [COLUMNS] sections, the [OVERRIDE] section takes priority

#### [SKIP_RECORDS]
This section handles whether a skip_record indicator is included in the CSV file.

For record skipping to be enabled, skip_records must be set to 'TRUE'.

Once enabled, both the skip_record_indicator column must be present (defined by 'skip_record_column') and must contain 
one of the items in the comma-separated list of indicators (defined by 'skip_record_indicator').

#### [OVERRIDE]
Columns in the CSV can be overridden with static data.  For overrides to occur, the field name must appear in this
section.  This allows a common value to be applied to all records in the CSV.

#### [COLUMNS]
This section gives the column number of the CSV to use for each required field, starting with 0 for the first column.

### CSV File

Example:

```
<unread_value>, John, Smith, johnsmith@email.com, Teacher, 1234, Farringham Road, England, <unread_value>, TAR;DIS, <unread_value>, OK
```

