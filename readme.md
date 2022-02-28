# Create Users from CSV file

Create Qualys user accounts from user information stored in a CSV file
The CSV file has the following column order
<unread value>, forename, surname, email, job title, phone, address1, country, asset_groups*

*asset groups are semi-colon delimited

example:

```
<unread_value>, John, Smith, johnsmith@email.com, Teacher, 1234, Farringham Road, England, <unread_value>, TAR;DIS, <unread_value>, OK
```
* The external_id value will be set to the same as the email address
* The business unit of the user account will be set to 'Unassigned'
* The city of the user will be set to 'London'
* If the item in column 11 of any given row is not 'OK', the row will be skipped

```
usage: create_users_from_csv.py [-h] [-f FILENAME] [-e] [-u USERNAME] [-p PASSWORD] [-P] [-U PROXY_URL] [-a APIURL] [-n] [-d] [-x]

options:                                                                                                                          
  -h, --help            show this help message and exit                                                                           
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
