"""File that wraps http requests to github api"""
import collections
import logging

import requests


LOG = logging.getLogger("hubsync.api")

Fork = collections.namedtuple('Fork', 'name description fork_owner origin_url'
                                      ' forked_url')


class Repo(object):
    """Represents a repo within github"""

    @staticmethod
    def from_url(api, url):
        """Builds an repo given its github api url"""
        data = api.get(url)
        return Repo(api, data["owner"]["login"], data["name"],
                    data["description"], data["ssh_url"], data["forks_url"])

    def __init__(self, api, user, name, description, url, forks_url):
        self.api = api
        self.user = user
        self.name = name
        self.description = description
        self.url = url
        self._forks_url = forks_url

    @property
    def forks(self):
        """Lists of the forks  of the repo"""
        result = self.api.get(self._forks_url)
        return [Fork(item["name"], item["description"], self.name,
                     item["ssh_url"], self.url) for item in result]


class Organization(object):
    """Represents an organization"""

    @staticmethod
    def from_url(api, url):
        """Builds an organization given its github api url"""
        data = api.get(url)
        return Organization(api, url, data["login"], data["description"],
                            data["repos_url"])

    def __init__(self, api, url, name, description, repos_url):
        """Builds the organization data given its url"""
        self.api = api
        self.url = url
        self.name = name
        self.description = description
        self.repos_url = repos_url

    def __repr__(self):
        """repr for an Organization"""
        return "<{0.__class__.__name__} {0.name}({0.description})>".format(self)

    @property
    def repos(self):
        """Retrieves the list of repos within an org"""
        result = self.api.get(self.repos_url)
        return [Repo.from_url(self.api, item["url"]) for item in result]


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
        return [Organization.from_url(self, item["url"]) for item in result]
