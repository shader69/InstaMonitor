import os.path
import json
import argparse
import requests

from json import decoder
from tabulate import tabulate
from datetime import date
from os.path import exists

# Prepare global variables
mode = 'prod'
show_color = True
maxUserRequested = 200
root = os.path.abspath(os.path.dirname(__file__))
session_path = os.path.join(root, 'data/session.txt')
histo_path = None
user_list_path = None

# Check arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help="Instagram username to get data", required=True)
parser.add_argument('-s', '--sessionid', help="Id sessions of Instagram web session", required=False)
parser.add_argument('-m', '--mode', help="Can be 'debug' or 'prod', for show warning messages", required=False)

args = parser.parse_args()

# Check args
if args.mode is not None:
    mode = args.mode


# Define fies paths
def defFilesPaths(user_id):

    # Create data path if not exist
    data_path = os.path.join(root, f'data')
    data_path_exist = os.path.exists(data_path)
    if not data_path_exist:
        os.makedirs(data_path)

    # Create user_path if not exist
    user_path = os.path.join(root, f'data/{user_id}')
    user_path_exist = os.path.exists(user_path)
    if not user_path_exist:
        os.makedirs(user_path)

    # Define files names
    global histo_path
    histo_path = os.path.join(root, f'data/{user_id}/histo.txt')

    global user_list_path
    user_list_path = os.path.join(root, f'data/{user_id}/users.txt')

# Get user instagram name
def getUsername():
    # If there is no arg
    if args.username is None:
        exit("Error: you must set username by args")

    # Else if there is argument
    elif args.username is not None:
        return args.username


# Get user instagram id
def getUserId(username):

    # Prepare 'get' variables
    session_id = getSessionId()
    cookies = {'sessionid': session_id}
    headers = {'User-Agent': 'Instagram 64.0.0.14.96'}

    # Check 'get' request
    api = requests.get(
        f'https://www.instagram.com/{username}/?__a=1&__d=dis',
        headers=headers,
        cookies=cookies
    )
    try:
        # Catch HTTP errors
        if api.status_code != 200:
            exit(f'Error: called URL return {api.status_code} error')

        if api.status_code == 404:
            exit(f'Error: user not founded')
        elif api.status_code != 200:
            exit(f'Error: called URL return {api.status_code} error')

        # Else, return data
        id = api.json()["logging_page_id"].strip("profilePage_")
        return id

    except decoder.JSONDecodeError:
        exit('Error: rate limit')


# Get session id by args or by file
def getSessionId():

     # If there is no arg and no session file
    if args.sessionid is None and not exists(session_path):
        exit("Error: you must set session id by args for the first opening")

    # Else if there is argument
    elif args.sessionid is not None:
        return args.sessionid

    # Else if there is session file
    elif exists(session_path):
        f = open(session_path, "r")
        return f.read()

    # That can't append, but for security we manage this case
    else:
        exit("Error on check session id")


# Save session id in session file
def saveSessionId(session_id):

    # Create the file if it does not exist, and open it in write mode
    f = open(session_path, 'w+')
    f.write(session_id)
    f.close()


# Function to return followers or following list
def callFollowers(userType):

    # Prepare some variables
    username = getUsername()
    user_id = getUserId(username)
    session_id = getSessionId()
    defFilesPaths(user_id)

    # Prepare 'get' variables
    cookies = {'sessionid': session_id}
    headers = {'User-Agent': 'Instagram 64.0.0.14.96'}

    # Check if wanted user type is correct
    if userType == 'followers':
        url = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count={maxUserRequested}&search_surface=follow_list_page'
    elif userType == 'following':
        url = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?count={maxUserRequested}'
    else:
        exit(f'Error: unrecognized user type "{userType}"')

    # Check 'get' request
    api = requests.get(
        url,
        headers=headers,
        cookies=cookies
    )
    try:
        # Catch HTTP errors
        if api.status_code != 200:
            exit(f'Error: called URL return {api.status_code} error')

        # Check if result is null
        elif len(api.json()["users"]) == 0:
            print(f'\u001b[33mWARNING: this user has no {userType}, or we are unable to get them.')
            print(f'    Please make sure that the sessionid corresponds to the username provided.\u001b[0m')

        # Else, save session id and return correct result
        saveSessionId(session_id)
        return api.json()["users"]

    except decoder.JSONDecodeError:
        exit('Error: rate limit')


# Fill histo file
def fillHistoFile(data_to_insert):

    # Check if input variable is an array, else we convert it
    if not isinstance(data_to_insert, list):
        data_to_insert = [data_to_insert]

    # Create the file if it does not exist, and open it in append mode
    f = open(histo_path, 'a+')

    # Get today's date (YYYY-mm-dd)
    today = date.today()

    # Loop on each data
    for data in data_to_insert:

        # Check if the data is correctly filled
        if not all(k in data for k in ("username", "he_follow_me", "i_follow_him", "date")):
            break

        # Check if this data not already exist in histo
        last_action_saved = searchInHistoFile(data["username"], True, True)

        if last_action_saved and last_action_saved["action_date"] == str(today):
            break

        # Prepare string to write
        string = '{'
        string += f'"username": "{data["username"]}", '
        string += f'"he_follow_me": {str(data["he_follow_me"]).lower()}, '
        string += f'"i_follow_him": {str(data["i_follow_him"]).lower()}, '
        string += f'"action_date": "{data["date"]}"'
        string += '},\n'

        # Append data
        f.write(string)

    # Close file
    f.close()


# Search user data in histo file
def searchInHistoFile(username, get_only_last_action=True, get_today_actions=False):

    # Return null if file not exist
    if not exists(histo_path):
        return

    # Get today's date (YYYY-mm-dd)
    today = date.today()

    # Open file
    f = open(histo_path, "r")

    # Prepare data, for convert in JSON
    file_prepared = '[' + f.read()

    if file_prepared.endswith(',\n'):
        file_prepared = file_prepared[:-2]

    file_prepared += ']'

    # Convert in JSON
    filedata = json.loads(file_prepared)

    # Loop on each histo line
    userdata = []
    for x in filedata:
        if x["username"] == username:
            userdata.append(x)

    # Close file
    f.close()

    # Remove today's action if necessary
    if not get_today_actions:
        userdata = list(filter(lambda d: d['action_date'] != str(today), userdata))

    # Return null if no data founded
    if not userdata:
        return

    # Get last action for this user
    if get_only_last_action:
        userdata = sorted(userdata, key=lambda d: d['action_date'])
        userdata = list(reversed(userdata))[0]

    return userdata


# Fill user list file
def fillUserList(username):

    # At first, check if user is not already in file
    userIsInFile = searchInUserList(username)

    if userIsInFile:
        return

    # Create the file if it does not exist, and open it in append mode
    f = open(user_list_path, 'a+')

    # Append data
    f.write(username + "\n")

    # Close file
    f.close()


# Search user data in user list file
def searchInUserList(username):

    # Return null if file not exist
    if not exists(user_list_path):
        return False

    # Open file
    f = open(user_list_path, "r")

    # Search if user is in file
    return username+"\n" in f


# Return user list file content, in list format
def getUserList():

    # Return null if file not exist
    if not exists(user_list_path):
        return []

    # Open file
    f = open(user_list_path, "r")

    # Convert in list, and remove \n
    return [line[:-1] for line in f.readlines()]


# Main execution
def main():

    # Start the script with a waiting message
    print('\nIn progress...')

    # Get followers list
    if mode == 'debug': print('Get followers...')
    followers = callFollowers('followers')
    followers = [d['username'] for d in followers]

    # Get following list
    if mode == 'debug': print('Get followings...')
    followings = callFollowers('following')
    followings = [d['username'] for d in followings]

    # If we can get followers and followings, thrown an error
    if len(followers) == 0 and len(followings) == 0:
        exit('Error: no followers and followings have been founded. '
             'Please make sure that the sessionid corresponds to the username provided.')

    # Get saved user list, for compare if there is missing users in followers and followings
    if mode == 'debug': print('Get saved users...')
    saved_users = getUserList()

    # Merge the two arrays, + saved user list, and remove double data
    merged_array = list(set(followers + followings + saved_users))

    # Prepare data to show
    data_to_show = []

    # Prepare data to save, in histo file
    data_to_save = []

    if mode == 'debug': print('Prepare data to show...')
    for username in merged_array:

        # Add user in user list file, if it not already exist
        fillUserList(username)

        # Prepare vars
        username_to_show = username
        i_follow_him = False
        he_follow_me = False
        save_this_action = False
        date_to_save = date.today()

        if username in followings:
            i_follow_him = True

        if username in followers:
            he_follow_me = True

        if i_follow_him and not he_follow_me:
            username_to_show = f'\u001b[31m{username}\u001b[0m'
        elif not i_follow_him and he_follow_me:
            username_to_show = f'\u001b[33m{username}\u001b[0m'

        # Check if this change has been saved in histo file
        last_action_date = ''
        last_action = searchInHistoFile(username)

        # If an action has been founded for this user
        if last_action:

            # Store date
            last_action_date = last_action['action_date']

            if last_action['he_follow_me'] != he_follow_me:
                save_this_action = True
                last_action_date = '\u001b[31mTODAY\u001b[0m'
            elif last_action['i_follow_him'] != i_follow_him:
                save_this_action = True
                last_action_date = '\u001b[33mTODAY\u001b[0m'
            elif last_action_date == "1970-01-01":
                last_action_date = ''
        else:
            date_to_save = "1970-01-01"
            save_this_action = True

        # Check if we save this data in history file
        if save_this_action:
            data_to_save.append({"username": username, "he_follow_me": he_follow_me, "i_follow_him": i_follow_him, "date": date_to_save})

        # Fill data to show
        data_to_show.append([username_to_show, i_follow_him, he_follow_me, last_action_date])

    # Fill histo
    fillHistoFile(data_to_save)

    # Order dict
    data_to_show = sorted(data_to_show, key=lambda d: d[0])

    # Show data
    print('\n')
    print(tabulate(data_to_show, headers=["Username", "I follow him", "He follow me", "Last check date"], tablefmt='github'))
    print('\n')

    # Show some counters
    print('-' * 45)

    users_not_following_me = [user for user in followings if user not in followers]
    print(f'Total users who do not follow you :    \u001b[31m{len(users_not_following_me)}\u001b[0m')

    users_i_dont_follow = [user for user in followers if user not in followings]
    print(f'Total users you don\'t follow :         \u001b[33m{len(users_i_dont_follow)}\u001b[0m')

    print('-' * 45)