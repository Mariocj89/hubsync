"""File wrapping workspace related functions"""
import logging
import os

import git

LOG = logging.getLogger('hubsync.workspace')


class Workspace(object):
    """Represents the current workspace directory"""
    def __init__(self, path):
        self.path = path

    @property
    def organizations(self):
        """Returns the organizations within the workspace"""
        try:
            return [Organization(subdir, self.path)
                    for subdir in next(os.walk(self.path))[1]]
        except StopIteration:
            return []


class Repo(object):
    """Repository representation within the workspace"""

    def __init__(self, name, base_path):
        """ Creates the repo object

        :type name: str
        :param name: name of the repository
        """
        self.name = name.rstrip('/')
        self.path = base_path + '/' + name
        self.git = git.Repo(self.path)

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
        self.path = base_path + '/' + name

    def __repr__(self):
        """repr for an Organization"""
        return "<{0.__class__.__name__} {0.name}({0.path})>".format(self)

    @property
    def repos(self):
        """All repos within the organization"""
        try:
            return [Repo(subdir, self.path)
                    for subdir in next(os.walk(self.path))[1]]
        except StopIteration:
            return []
