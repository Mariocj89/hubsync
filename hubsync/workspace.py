"""File wrapping workspace related functions"""
import logging
import os

import git

LOG = logging.getLogger('hubsync.workspace')


class LocalWorkspaceError(Exception):
    """Base exception for errors related to the local file workspace"""


class InvalidPath(LocalWorkspaceError):
    """Raised when a repository/org is attempted to be read in a path where it
    does not exist"""


def get_sub_folders(path):
    """Returns the name of all subfolders within a path"""
    return next(os.walk(path))[1]


class Workspace(object):
    """Represents the current workspace directory"""
    def __init__(self, path):
        self.path = path

    @property
    def organizations(self):
        """Returns the organizations within the workspace"""
        try:
            return [Organization(subdir, self.path)
                    for subdir in get_sub_folders(self.path)]
        except StopIteration:
            raise InvalidPath("Unable to search for orgs within {0.path}, "
                              "is the path correct?".format(self))

    def __repr__(self):
        return "<{0.__class__.__name__} ({0.path})>".format(self)


class Repo(object):
    """Repository representation within the workspace"""

    def __init__(self, name, base_path):
        """ Creates the repo object

        :type name: str
        :param name: name of the repository
        """
        self.name = name.rstrip('/')
        self.path = os.path.join(base_path, self.name)
        try:
            self.git = git.Repo(self.path)
        except git.exc.InvalidGitRepositoryError:
            raise InvalidPath("Git repo don't exists in path {}".format(
                self.path))

    def __repr__(self):
        """repr for an Repo"""
        return "<{0.__class__.__name__} {0.name}({0.path})>".format(self)


class Organization(object):
    """Workspace representation of an organization

    This class contains models how we store an organization in the user's local
    workspace
    """

    def __init__(self, name, base_path):
        """Creates the organization object

        :type name: str
        :param name: name of the organization
        """
        self.name = name.rstrip('/')
        self.path = os.path.join(base_path, self.name)

    def __repr__(self):
        """repr for an Organization"""
        return "<{0.__class__.__name__} {0.name}({0.path})>".format(self)

    @property
    def repos(self):
        """All repos within the organization"""
        try:
            # Note get_sub_folders use os.walk, which means that you should not
            # change the current working dir whilst generating the list of repos
            return [Repo(subdir, self.path)
                    for subdir in get_sub_folders(self.path)]
        except StopIteration:
            raise InvalidPath("Unable to search for repos within org {0.name}, "
                              "is path {0.path} correct?".format(self))
