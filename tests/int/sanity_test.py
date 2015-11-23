"""Sanity tests"""
from collections import defaultdict
import os
import shutil
import unittest
import subprocess
import ConfigParser

import mock
from hubsync import sync, github, workspace


def gb_api_mock(responses, default_=None):
    """Mock helper for github api, returns a function ready for mocking

    Given a dictionary of the last token of the url and the response can be
    user to mock the github api. A default value can be provided if none matches

    See an example in the tests, it is indented to patch Api.get
    """

    def mocked_get(url):
        try:
            return responses[url.split('/')[-1]]
        except KeyError:
            if default_:
                return default_
            else:
                raise
    return mocked_get


class SanityTestCase(unittest.TestCase):
    """Sanity Tests to guarantee the basics of the script

    It runs the tests by monkey patching the github api calls and  working in
    a local workspace within a temp folder
    """

    def _create_local_org(self, name):
        """Creates a folder that represents an org locally"""
        os.makedirs(os.path.join(self.path, name))

    def setUp(self):
        self.base_url = 'base'
        self.path = subprocess.check_output('mktemp -d',
                                            shell=True).splitlines()[0]
        print("Running tests in " + self.path)
        self.gh_api = github.Api(api_url=self.base_url, user_token='')
        self.ws = workspace.Workspace(self.path)
        # we should create a wrapper on top of config parser
        self.config = ConfigParser.ConfigParser(defaults={
            'pre': [],
            'post': [],
        })
        self.config.add_section('org')
        self.config.add_section('repo')
        self.syncer = sync.SyncHelper(self.gh_api, self.config)

    def tearDown(self):
        shutil.rmtree(self.path)

    @mock.patch('hubsync.github.Api.get')
    def test_no_org_nor_repo_empty_ws(self, api_get):
        """Test a user with no repo makes no change to an empty ws"""
        api_get.side_effect = gb_api_mock({
            'orgs': []
        }, {})

        self.syncer.sync(self.ws, self.gh_api)

        # no dirs
        self.assertEqual([], next(os.walk(self.path))[1])
        # no files
        self.assertEqual([], next(os.walk(self.path))[2])

    @mock.patch('hubsync.github.Api.get')
    def test_empty_org_already_synced_does_nothing(self, api_get):
        """Test a user with a repo locally already synced makes no change"""
        org_name = 'sample_org'
        api_get.side_effect = gb_api_mock({
            'orgs': [defaultdict(str, {
                'url': 'org_url'
            })],
            'org_url': defaultdict(str, {
                'login': org_name,
                'repos_url': 'repos_url'
            }),
            'repos_url': []
        }, {})
        self._create_local_org(org_name)

        self.assertEqual(['sample_org'], next(os.walk(self.path))[1])
        path_before = list(os.walk(self.path))

        self.syncer.sync(self.ws, self.gh_api)

        path_after = list(os.walk(self.path))
        # same result as before the run
        self.assertEqual(path_before, path_after)
