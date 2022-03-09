import csv
from xml.etree import ElementTree as ET
import QualysAPI
import argparse
import sys
import getpass
import os.path
import configparser


def validate_api_response(response: ET.ElementTree):
    if response.find('.//RETURN').attrib['status'] == 'SUCCESS':
        return 0, ''
    else:
        return 2, response.find('.//MESSAGE').text


def my_quit(exitcode: int, errormsg: str = None):
    if exitcode != 0:
        print('ERROR', end='')
        if errormsg is None:
            print('')
        else:
            print(' %s' % errormsg)
    sys.exit(exitcode)


class QualysUser:
    forename: str
    surname: str
    email: str
    title: str
    phone: str
    address1: str
    city: str
    country: str
    external_id: str
    asset_groups: list
    business_unit: str

    def create_url(self, baseurl: str, send_email: bool = False, user_role: str = 'reader'):
        url = '%s/msp/user.php' % baseurl
        payload = {
            'action': 'add',
            'first_name': self.forename,
            'last_name': self.surname,
            'title': self.title,
            'phone': self.phone,
            'email': self.email,
            'address1': self.address1,
            'city': self.city,
            'country': self.country,
            'user_role': user_role,
            'asset_groups': ','.join(self.asset_groups),
            'business_unit': self.business_unit
        }
        if send_email:
            payload['send_email'] = '1'
        else:
            payload['send_email'] = '0'

        return url, payload


if __name__ == '__main__':
    # Add arguments to be collected from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', help='Input CSV file containing user information')
    parser.add_argument('-e', '--no_send_email', action='store_true', help='Do Not Send Email for user registration')
    parser.add_argument('-u', '--username', help='Qualys Username')
    parser.add_argument('-p', '--password', help='Qualys Password (use - for interactive input')
    parser.add_argument('-P', '--proxy_enable', action='store_true', help='Enable HTTPS proxy')
    parser.add_argument('-U', '--proxy_url', help='HTTPS proxy address')
    parser.add_argument('-a', '--apiurl', help='Qualys API URL (e.g. https://qualysapi.qualys.com)')
    parser.add_argument('-n', '--no_call', action='store_true', help='Do not make API calls, write URLs to console')
    parser.add_argument('-d', '--debug', action='store_true', help='Provide debugging output from API calls')
    parser.add_argument('-x', '--exit_on_error', action='store_true', help='Exit on error')

    # Process the passed arguments
    args = parser.parse_args()

    # Validate the critical arguments
    if args.filename is None or args.filename == '':
        my_quit(1, 'CSV File Not Specified')

    if not os.path.exists(args.filename):
        my_quit(1, 'CSV File %s does not exist' % args.filename)

    if not os.path.isfile(args.filename):
        my_quit(1, '%s is not a file' % args.filename)

    if args.username is None or args.username == '':
        my_quit(1, 'Username not specified')

    if args.password is None or args.password == '':
        my_quit(1, 'Password not specified or - not used in password option')

    if args.proxy_enable and (args.proxy_url is None or args.proxy_url == ''):
        my_quit(1, 'Proxy enabled but proxy URL not specified')

    if args.apiurl is None or args.apiurl == '':
        my_quit(1, 'API URL not specified')

    # Get the Password interactively if '-' is used in that argument
    if args.password == '-':
        password = getpass.getpass(prompt='Enter password : ')
    else:
        password = args.password

    if args.proxy_enable:
        api = QualysAPI.QualysAPI(svr=args.apiurl, usr=args.username, passwd=password, enableProxy=args.proxy_enable,
                                  proxy=args.proxy_url, debug=args.debug)
    else:
        api = QualysAPI.QualysAPI(svr=args.apiurl, usr=args.username, passwd=password, debug=args.debug)

    with open(args.filename, 'r') as inputfile:
        csvreader = csv.reader(inputfile, delimiter=',', quotechar='"')

        for row in csvreader:
            if row[11] == 'OK':
                user = QualysUser()
                user.forename = row[1]
                user.surname = row[2]
                user.email = row[3]
                user.title = row[4]
                user.phone = row[5]
                user.address1 = row[6]
                user.city = 'London'
                user.country = row[7]
                user.asset_groups = row[9].split(';')
                user.external_id = row[3]
                user.business_unit = 'Unassigned'

                url, payload = user.create_url(baseurl=api.server, send_email=not args.no_send_email,
                                               user_role='reader')

                response = api.makeCall(url=url, payload=payload)
                error_code, error_message = validate_api_response(response=response)
                if error_code > 0 and args.exit_on_error:
                    my_quit(exitcode=error_code, errormsg='Could not create user %s %s (%s) : Reason (%s)' %
                                                          (user.forename,
                                                           user.surname,
                                                           user.email,
                                                           error_message))
                elif error_code > 0:
                    print('ERROR: Could not create user %s %s (%s) : Reason (%s)' % (user.forename, user.surname,
                                                                                     user.email, error_message))
                else:
                    username = response.find('.//USER_LOGIN').text
                    print('User %s (%s %s) Created' % (username, user.forename, user.surname))

            else:
                print('Skipping INCOMPLETE entry for %s %s' % (row[1], row[2]))
