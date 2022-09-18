from project.globals import *

from project.connected_user import ConnectedUser
from project.targeted_user import TargetedUser

from tabulate import tabulate
from datetime import date
import os.path
import colorama


def main(targeted_username, connected_user_session_id=None):
    """
    Main function
    :param targeted_username: string
    :param connected_user_session_id: string
    :return: show a table
    """
    global root
    global show_log

    # Init colorama
    colorama.init(wrap=True)

    # Create data path if not exist
    data_path = os.path.join(root, f'data')
    data_path_exist = os.path.exists(data_path)
    if not data_path_exist:
        os.makedirs(data_path)

    # Instantiate ConnectedUser
    connected_user = ConnectedUser(connected_user_session_id)

    # Instantiate TargetedUser
    targeted_user = TargetedUser(connected_user, targeted_username)

    # Start the script with a waiting message
    print('\nIn progress...')

    # Get followers list
    print('Get followers...')
    followers = targeted_user.followers.api_get_followers('followers')

    # Get following list
    print('Get followings...')
    followings = targeted_user.followers.api_get_followers('following')

    # If we can't get followers and followings, thrown an error
    if len(followers) == 0 and len(followings) == 0:
        exit('Error: no followers and followings have been founded. '
             'Please make sure that the sessionid\'s user is allowed to view wanted user content.')

    # Get saved user list, for compare if there is missing users in followers and followings
    print('Get saved users...')
    saved_users = targeted_user.followers.get_followers_file_content()

    # Merge the two arrays, + saved user list, and remove double data
    merged_array = list(set(followers + followings + saved_users))

    # Prepare data to show
    data_to_show = []

    # Prepare data to save, in histo file
    data_to_save = []

    print('Prepare data to show...')

    for username in merged_array:

        # Add user in user list file, if it not already exist
        targeted_user.followers.fill_followers_file(username)

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
        last_action = targeted_user.history.search_in_histo_file(username)

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
    targeted_user.history.fill_histo_file(data_to_save)

    # Order dict
    data_to_show = sorted(data_to_show, key=lambda d: d[0])

    # Show data
    print('\n')
    print(tabulate(data_to_show, headers=["Username", "I follow him", "He follow me", "Last check date"], tablefmt='github'))
    print('\n')

    # Show some counters
    print('-' * 45)

    print(f'Total users :                      {len(merged_array)}')

    users_not_following_me = [user for user in followings if user not in followers]
    print(f'Followings who do not follow you : \u001b[31m{len(users_not_following_me)}\u001b[0m / {len(followings)}')

    users_i_dont_follow = [user for user in followers if user not in followings]
    print(f'Followers you don\'t follow :       \u001b[33m{len(users_i_dont_follow)}\u001b[0m / {len(followers)}')

    print('-' * 45)
