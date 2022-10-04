from instamonitor.globals import *
import os
from os.path import exists


class ConnectedUser:
    """
    Class used for a user connected to the app.

    Attributes
    ----------
    session_path : str
        the path to session file
    session_id : str
        the connected user session id

    Methods
    -------
    set_session_path()
        Set file path to session file.
    get_session_id(arg_sessionid=None)
        Get connected user session ID, by args or file.
    save_session_id()
        Save connected user session ID in file.
    set_session_id(session_id)
        Set session_id variable to instance.
    """

    session_path = None
    session_id = None

    def __init__(self, arg_sessionid=None):
        """
        Init instance
        :param arg_sessionid: string, object from argparse class
        :return: Void
        """

        # Manage session
        self.set_session_path()
        session_id = self.get_session_id(arg_sessionid)
        self.set_session_id(session_id)

    def set_session_path(self):
        """
        Set file path to session file
        :return: void
        """
        global root

        if root is None:
            exit("Undefined variable 'root' in ConnectedUser class.")

        # Set variable
        self.session_path = os.path.join(root, 'data/session.txt')

        # We don't create session file if not exist, because we need to know
        # if the file has been created or not

    def get_session_id(self, arg_sessionid=None):
        """
        Get connected user session ID, by args or file
        :param arg_sessionid : string, object from argparse class
        :return: string
        """

        # If there is no arg and no session file
        if arg_sessionid is None and not exists(self.session_path):
            exit("Error: you must set session id by args for the first opening")

        # Else if there is argument
        elif arg_sessionid is not None:
            return arg_sessionid

        # Else if there is session file
        elif exists(self.session_path):
            f = open(self.session_path, "r")
            return f.read()

        # That can't append, but for security we manage this case
        else:
            exit("Error on check session id")

    def save_session_id(self):
        """
        Save connected user session ID in file
        :return: void
        """
        # Create the file if it does not exist, and open it in write mode
        f = open(self.session_path, 'w+')
        f.write(self.session_id)
        f.close()

    def set_session_id(self, session_id):
        """
        Set variable to instance
        :param session_id: string
        :return: void
        """
        self.session_id = session_id
