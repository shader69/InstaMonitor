from project.globals import *
import os.path
import json
from datetime import date
from os.path import exists


class History:
    """
    Class for access history file, for a TargetedUser.

    Attributes
    ----------
    histo_path : str
        the path to history file
    histo_file_data : list
        contain file data, for don't reopen file each time
    targeted_user : instance of TargetedUser class
        for get history path

    Methods
    -------
    set_histo_path()
        Set file path to histo file.
    fill_histo_file(data_to_insert)
        Fill data into histo file.
    read_histo_file()
        Open histo file, and prepare all data in an array.
    search_in_histo_file(username, get_only_last_action=True, get_today_actions=False)
        Search user data in histo array.
    """

    histo_path = None
    histo_file_data = []
    targeted_user = None

    def __init__(self, TargetedUser):
        """
        Init class
        :param TargetedUser: instance of TargetedUser class
        """

        # Set TargetedUser
        self.targeted_user = TargetedUser

        # Manage history path
        self.set_histo_path()

        # Store file data
        self.histo_file_data = self.read_histo_file()

    def set_histo_path(self):
        """
        Set file path to histo file
        :return: void
        """
        global root

        if root is None:
            exit("Undefined variable 'root' in History class.")

        # Set variable
        self.histo_path = os.path.join(root, f'data/{self.targeted_user.user_id}/histo.txt')

    def fill_histo_file(self, data_to_insert):
        """
        Fill data into histo file
        :param data_to_insert: list of dict, contain data to insert
        :return: void
        """

        # Check if input variable is an array, else we convert it
        if not isinstance(data_to_insert, list):
            data_to_insert = [data_to_insert]

        # Create the file if it does not exist, and open it in append mode
        f = open(self.histo_path, 'a+')

        # Get today's date (YYYY-mm-dd)
        today = date.today()

        # Loop on each data
        for data in data_to_insert:

            # Check if the data is correctly filled
            if not all(k in data for k in ("username", "he_follow_me", "i_follow_him", "date")):
                break

            # Check if this data not already exist in histo
            last_action_saved = self.search_in_histo_file(data["username"], True, True)

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

    def read_histo_file(self):
        """
        Open histo file, and prepare all data in an array
        :return: list of dict, contain all file data
        """

        # Return null if file not exist
        if not exists(self.histo_path):
            return []

        # Open file
        f = open(self.histo_path, "r")

        # Prepare data, for convert in JSON
        file_prepared = '[' + f.read()

        if file_prepared.endswith(',\n'):
            file_prepared = file_prepared[:-2]

        file_prepared += ']'

        # Convert in JSON
        file_prepared_formatted = json.loads(file_prepared)

        # Loop on each histo line
        global_user_data = {}
        for line in file_prepared_formatted:

            # If data for this used hasn't already been saved
            if not line["username"] in global_user_data:
                global_user_data[line["username"]] = []

            # Fill this user array data
            global_user_data[line["username"]].append(line)

        # Close file
        f.close()

        # Return prepared array
        return global_user_data

    def search_in_histo_file(self, username, get_only_last_action=True, get_today_actions=False):
        """
        Search user data in histo array
        :param username: search in histo data for this username
        :param get_only_last_action: bool
        :param get_today_actions: bool
        :return: list of dict
        """

        # Return null if file not exist
        if not exists(self.histo_path):
            return

        # Get today's date (YYYY-mm-dd)
        today = date.today()

        # Check if there is data for this user
        if username not in self.histo_file_data:
            return

        # Else, get user data
        userdata = self.histo_file_data[username]

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
