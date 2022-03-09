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
    time_zone_code: str

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
            'business_unit': self.business_unit,
            'time_zone_code': self.time_zone_code
        }
        if self.external_id is not None:
            payload['external_id'] = self.external_id

        if send_email:
            payload['send_email'] = '1'
        else:
            payload['send_email'] = '0'

        return url, payload


if __name__ == '__main__':
    # Add arguments to be collected from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Configuration file name (default: config.ini)')
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

    # Validate the configuration file
    config_file = 'config.ini'
    if args.config is not None:
        if os.path.exists(args.config) and os.path.isfile(args.config):
            config_file = args.config
        else:
            my_quit(1, 'Config file does not exist or is not a file: %s' % args.config)

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

    # Process the configuration file

    config = configparser.ConfigParser()
    config.read(config_file)
    if 'COLUMNS' not in config.keys():
        my_quit(1, '[COLUMNS] section not found in configuration file %s' % config_file)

    if 'OVERRIDE' not in config.keys():
        my_quit(1, '[OVERRIDE] section not found in configuration file %s' % config_file)

    if 'SKIP_RECORDS' not in config.keys():
        my_quit(1, '[SKIP_RECORDS] section not found in configuration file %s' % config_file)

    config_default = config['COLUMNS']
    config_override = config['OVERRIDE']
    config_skip = config['SKIP_RECORDS']

    for i in ['forename', 'surname', 'email', 'title', 'phone', 'address1', 'city', 'country', 'asset_groups',
              'time_zone_code', 'external_id', 'business_unit']:
        if i not in config_default.keys() and i not in config_override.keys():
            my_quit(1, 'Configuration item \'%s\' not found in configuration file' % i)

    if args.proxy_enable:
        api = QualysAPI.QualysAPI(svr=args.apiurl, usr=args.username, passwd=password, enableProxy=args.proxy_enable,
                                  proxy=args.proxy_url, debug=args.debug)
    else:
        api = QualysAPI.QualysAPI(svr=args.apiurl, usr=args.username, passwd=password, debug=args.debug)

    skip_records = False
    skip_record_column = 9999999
    skip_record_indicator = None
    if 'skip_records' in config_skip.keys():
        if config_skip['skip_records'].lower() == 'true':
            skip_records = True
            if 'skip_record_indicator' not in config_skip.keys() or 'skip_record_column' not in config_skip.keys():
                my_quit(1, '[SKIP_RECORDS] section incomplete, must include \'skip_record_indicator\' and '
                           '\'skip_record_column\'')
            skip_record_indicator = config_skip['skip_record_indicator'].split(',')
            skip_record_column = int(config_skip['skip_record_column'])

    with open(args.filename, 'r') as inputfile:
        csvreader = csv.reader(inputfile, delimiter=',', quotechar='"')

        for row in csvreader:

            if skip_records and row[skip_record_column] not in skip_record_indicator:
                user = QualysUser()
                if 'forename' in config_override.keys():
                    user.forename = config_override['forename']
                else:
                    if config_default['forename'] == 'override':
                        my_quit(1, 'Override not found: \'forename\'')
                    user.forename = row[int(config_default['forename'])]

                if 'surname' in config_override.keys():
                    user.surname = config_override['surname']
                else:
                    if config_default['surname'] == 'override':
                        my_quit(1, 'Override not found: \'surname\'')
                    user.surname = row[int(config_default['surname'])]

                if 'email' in config_override.keys():
                    user.email = config_override['email']
                else:
                    if config_default['email'] == 'override':
                        my_quit(1, 'Override not found: \'email\'')
                    user.email = row[int(config_default['email'])]

                if 'title' in config_override.keys():
                    user.title = config_override['title']
                else:
                    if config_default['title'] == 'override':
                        my_quit(1, 'Override not found: \'title\'')
                    user.title = row[int(config_default['title'])]

                if 'phone' in config_override.keys():
                    user.phone = config_override['phone']
                else:
                    if config_default['phone'] == 'override':
                        my_quit(1, 'Override not found: \'phone\'')
                    user.phone = row[int(config_default['phone'])]

                if 'address1' in config_override.keys():
                    user.address1 = config_override['address1']
                else:
                    if config_default['address1'] == 'override':
                        my_quit(1, 'Override not found: \'address1\'')
                    user.address1 = row[int(config_default['address1'])]

                if 'city' in config_override.keys():
                    user.city = config_override['city']
                else:
                    if config_default['city'] == 'override':
                        my_quit(1, 'Override not found: \'city\'')
                    user.city = row[int(config_default['city'])]

                if 'country' in config_override.keys():
                    user.country = config_override['country']
                else:
                    if config_default['country'] == 'override':
                        my_quit(1, 'Override not found: \'country\'')
                    user.country = row[int(config_default['country'])]

                if 'asset_groups' in config_override.keys():
                    user.asset_groups = config_override['asset_groups'].split(';')
                else:
                    if config_default['asset_groups'] == 'override':
                        my_quit(1, 'Override not found: \'asset_groups\'')
                    user.asset_groups = row[int(config_default['asset_groups'])].split(';')

                if 'external_id' in config_override.keys():
                    user.external_id = config_override['external_id']
                else:
                    if config_default['external_id'] == 'override':
                        my_quit(1, 'Override not found: \'external_id\'')
                    user.external_id = row[int(config_default['external_id'])]

                if 'business_unit' in config_override.keys():
                    user.business_unit = config_override['business_unit']
                else:
                    if config_default['business_unit'] == 'override':
                        my_quit(1, 'Override not found: \'business_unit\'')
                    user.external_id = row[int(config_default['business_unit'])]

                if 'time_zone_code' in config_override.keys():
                    user.time_zone_code = config_override['time_zone_code']
                else:
                    if config_default['time_zone_code'] == 'override':
                        my_quit(1, 'Override not found: \'time_zone_code\'')
                    user.time_zone_code = row[int(config_default['time_zone_code'])]

                url, payload = user.create_url(baseurl=api.server, send_email=not args.no_send_email,
                                               user_role='reader')
                if not args.no_call:
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
                    print('NO_CALL: Output URL and Payload\nURL: %s\nPAYLOAD: %s' % (url, payload))
            else:
                print('Skipping %s entry for %s %s' % (row[skip_record_column], row[1], row[2]))
