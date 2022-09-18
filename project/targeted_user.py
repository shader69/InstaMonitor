from project.globals import *
import os
import requests
from json import decoder
from project.followers import Followers
from project.history import History


class TargetedUser:
    """
    Class used for a user targeted by ConnectedUser

    Attributes
    ----------
    user_name : str
        the path to session file
    user_id : number
        connected user instagram's ID
    connected_user : instance of ConnectedUser class
        used for get xxx

    Methods
    -------
    get_user_name()
        Get user instagram's name.
    get_user_id()
        Get user instagram's ID.
    set_user_name(user_name)
        Set variable to instance.
    create_user_path()
        Create targeted user directory if not exist
    """

    user_name = None
    user_id = None
    connected_user = None

    def __init__(self, ConnectedUser, arg_username=None):
        """
        Init instance
        :param ConnectedUser: instance of ConnectedUser class
        :param arg_username: string, object from argparse class
        :return: void
        """

        # Set ConnectedUser
        self.connected_user = ConnectedUser

        # Manage user_name
        user_name = self.get_user_name(arg_username)
        self.set_user_name(user_name)

        # Manage user_id
        self.user_id = self.get_user_id()

        # Create user path if not exist
        self.create_user_path()

        # Instantiate Followers
        self.followers = Followers(self, ConnectedUser)

        # Instantiate History
        self.history = History (self)

    def get_user_name(self, arg_username):
        """
        Get user instagram name
        :param arg_username: string, object from argparse class
        :return: string
        """

        # If there is no args
        if arg_username is None:
            exit("Error: you must set username by args. Use '-u' argument.")

        # Else, do a special check for Instagram API
        elif arg_username in ["username", ""]:
            exit(f"Error: you can't search data for username '{arg_username}'.")

        # If no error, return username
        return arg_username

    def get_user_id(self):
        """
        Get user instagram's ID
        :return: string
        """
        # Prepare 'get' variables
        session_id = self.connected_user.session_id
        cookies = {'sessionid': session_id}
        headers = {'User-Agent': 'Instagram 64.0.0.14.96'}

        # Check 'get' request
        api = requests.get(
            f'https://www.instagram.com/{self.user_name}/?__a=1&__d=dis',
            headers=headers,
            cookies=cookies
        )
        try:
            # Catch HTTP errors
            if api.status_code == 404:
                exit(f'Error: user not founded.')
            elif api.status_code != 200:
                exit(f'Error: called URL return {api.status_code} error.')

            # Else, return data
            json_call = api.json()

            # Check if data is returned
            if json_call == {}:
                exit('Error: api call return no result. Please verify username to search.')

            return json_call["logging_page_id"].strip("profilePage_")

        except decoder.JSONDecodeError:
            exit('Error: rate limit, or incorrect session id. Try to refresh your session id.')

    def set_user_name(self, user_name):
        """
        Set variable to instance
        :param user_name: string
        :return: void
        """
        self.user_name = user_name

    def create_user_path(self):
        """
        Create targeted user directory if not exist
        :return: void
        """
        global root

        if root is None:
            exit("Undefined variable 'root' in TargetedUser class.")

        # Create targeted user path if not exist
        targeted_user_path = os.path.join(root, f'data/{self.user_id}')
        targeted_user_path_exist = os.path.exists(targeted_user_path)
        if not targeted_user_path_exist:
            os.makedirs(targeted_user_path)
