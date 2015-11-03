"""File that wraps http requests to github api"""
import collections
import logging

import requests

LOG = logging.getLogger("hubsync.api")

Repo = collections.namedtuple('Repo', 'user name description url')


class Organization(object):
    """Represents an organization"""

    def __init__(self, api, url):
        """Builds the organization data given its url"""
        self.api = api
        self.url = url
        result = self.api.get(url)
        self.name = result["login"]
        self.description = result["description"]
        self.repos_url = result["repos_url"]

    def __repr__(self):
        """repr for an Organization"""
        return "<{0.__class__.__name__} {0.name}({0.description})>".format(self)

    @property
    def repos(self):
        """Retrieves the list of repos within an org"""
        result = self.api.get(self.repos_url)
        # we can use ssh_url instead of url
        return [Repo(self.name, item["name"], item["description"],
                     item["ssh_url"]) for item in result]


class Api(object):
    """Class that wraps calls to github api"""

    def __init__(self, api_url, user_token):
        """Creates a wrapper for github api

        :param api_url: base url for github api
        :param user_token: user token to get access to github
        """
        self.base_url = api_url
        self.token = user_token

    def get(self, url):
        """Performs a get to an url passing the auth header"""
        return requests.get(url, headers={
            "Authorization": "token {}".format(self.token)
        }).json()

    @property
    def organizations(self):
        """Retrieves all organizations an user have"""
        result = self.get(self.base_url + "/user/orgs")
        return [Organization(self, item["url"]) for item in result]
