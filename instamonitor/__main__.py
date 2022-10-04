from instamonitor.core import *
import argparse

# Check arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help="Instagram username to get data", required=True)
parser.add_argument('-s', '--sessionid', help="Id sessions of Instagram web session", required=False)
parser.add_argument('-l', '--showlog', help="Can be 'true' or 'false', for show log messages", required=False)

args = parser.parse_args()

# Check args
if args.showlog is not None:
    if args.showlog == "true" or args.showlog == "True":
        show_log = True
    else:
        show_log = False


# Execute main function from setup.py
def main_for_setup():
    global args
    main(args.username, args.sessionid)
