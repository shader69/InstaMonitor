from project.globals import *
import os
from json import decoder
from os.path import exists
import requests
from project.history import History


class Followers:
    """
    Class used for access followers file, for a TargetedUser.

    Attributes
    ----------
    followers_path : str
        the path to followers file
    targeted_user : instance of TargetedUser class
        for get followers path
    connected_user : instance of ConnectedUser class
        for get followers path

    Methods
    -------
    set_followers_path()
        Set file path to followers file.
    fill_followers_file(username_to_add)
        Fill username in followers_path.
    search_in_followers_file(user_to_find)
        Search user data in user list file.
    get_followers_file_content()
        Return followers file content, in list format.
    """

    followers_path = None
    targeted_user = None
    connected_user = None
    history = None

    def __init__(self, TargetedUser, ConnectedUser):
        """
        Init class
        :param TargetedUser: instance of TargetedUser class
        :param ConnectedUser: instance of ConnectedUser class
        """

        # Set TargetedUser and ConnectedUser
        self.targeted_user = TargetedUser
        self.connected_user = ConnectedUser

        # Manage followers path
        self.set_followers_path()

        # Instantiate History
        self.history = History(self.targeted_user)

    def set_followers_path(self):
        """
        Set file path to followers file
        :return: void
        """
        global root

        if root is None:
            exit("Undefined variable 'root' in Followers class.")

        # Set variable
        self.followers_path = os.path.join(root, f'data/{self.targeted_user.user_id}/users.txt')

    def fill_followers_file(self, username_to_add):
        """
        Fill username in followers_path
        :param username_to_add: string
        :return: void
        """

        # At first, check if user is not already in file
        user_is_in_file = self.search_in_followers_file(username_to_add)

        if user_is_in_file:
            return

        # Create the file if it does not exist, and open it in append mode
        f = open(self.followers_path, 'a+')

        # Append data
        f.write(username_to_add + "\n")

        # Close file
        f.close()

    def search_in_followers_file(self, user_to_find):
        """
        Search user data in user list file
        :param user_to_find: string
        :return:
        """

        # Return null if file not exist
        if not exists(self.followers_path):
            return False

        # Open file
        f = open(self.followers_path, "r")

        # Search if user is in file
        return user_to_find+"\n" in f

    def get_followers_file_content(self):
        """
        Return followers file content, in list format
        :return: list
        """

        # Return null if file not exist
        if not exists(self.followers_path):
            return []

        # Open file
        f = open(self.followers_path, "r")

        # Convert in list, and remove \n
        return [line[:-1] for line in f.readlines()]

    def api_get_followers(self, user_type, big_data_check=True):
        """
        Call Instagram API, and Return followers or following list
        :param user_type: string, can be 'followers' or 'following'
        :param big_data_check: bool, if true and use_list is big, we loop another time, because sometime Instagram return incorrect data
        :return: list
        """
        # Prepare some variables
        max_followers_requested = 100   # can't be upper to 100
        max_query_loop_count = 10
        max_big_data_check_loop_count = 10
        global show_log

        # Prepare 'get' variables
        cookies = {'sessionid': self.connected_user.session_id}
        headers = {'User-Agent': 'Instagram 64.0.0.14.96'}

        # Check if wanted user type is correct
        if user_type == 'followers':
            url = f'https://i.instagram.com/api/v1/friendships/{self.targeted_user.user_id}/followers/?count={max_followers_requested}&search_surface=follow_list_page'
        elif user_type == 'following':
            url = f'https://i.instagram.com/api/v1/friendships/{self.targeted_user.user_id}/following/?count={max_followers_requested}'
        else:
            exit(f'Error: unrecognized user type "{user_type}".')

        # Prepare data to return
        users_data = []

        try:
            
            # Prepare a first loop, to manage big data if necessary
            big_data_loop_count = 0
            continue_big_data_loop_continue = True

            while continue_big_data_loop_continue:

                big_data_loop_count = big_data_loop_count + 1

                # Prepare to loop for query call
                query_loop_count = 0
                query_loop_continue = True
                next_max_id = None

                while query_loop_continue:
    
                    if show_log:
                        to_print = f'\u001b[33m   '
                        if big_data_check:
                            to_print = to_print + f'Big data loop n°{big_data_loop_count} : '

                        to_print = to_print + (f'Call {user_type} : {max_followers_requested*query_loop_count} to {max_followers_requested*(query_loop_count+1)}   \u001b[0m')
                        print(to_print)

                    query_loop_count = query_loop_count + 1
    
                    # Get more users if necessary
                    if next_max_id is not None:
                        current_url = url + '&max_id=' + next_max_id
                    else:
                        current_url = url
    
                    # Check 'get' request
                    api = requests.get(
                        url=current_url,
                        headers=headers,
                        cookies=cookies
                    )
    
                    # Catch HTTP errors
                    if api.status_code != 200:
                        exit(f'Error: called URL return {api.status_code} error.')
    
                    # Check if result is null
                    elif len(api.json()["users"]) == 0:
                        print(f'\u001b[33mWARNING: this user has no {user_type}, or we are unable to get them.')
                        print(f'    Please make sure that the sessionid\'s user is allowed to view wanted user content.\u001b[0m')

                    # Merge user list
                    users_data.extend(u['username'] for u in api.json()["users"] if 'username' in u)

                    # Remove double data
                    users_data = list(dict.fromkeys(users_data))
    
                    # If there is more users
                    if "next_max_id" not in api.json() or query_loop_count == max_query_loop_count:
                        query_loop_continue = False
                    elif "next_max_id" in api.json():
                        next_max_id = api.json()["next_max_id"]

                # Check if we need to continue loop
                if big_data_check and big_data_loop_count < len(users_data)/100 and big_data_loop_count < max_big_data_check_loop_count:
                    continue_big_data_loop_continue = True
                else:
                    continue_big_data_loop_continue = False

            # Save session id, because maybe it's work
            self.connected_user.save_session_id()

            if show_log: print(f'\u001b[33m   Users founded : {str(len(users_data))}   \u001b[0m')

            # Return correct result
            return users_data

        except decoder.JSONDecodeError:
            exit('Error: rate limit, or incorrect session id. Try to refresh your session id.')
