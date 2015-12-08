"""Simple Sanity tests

Simple sanity tests that target some specific features in hubsync.sync
"""
from collections import defaultdict
import os
import shutil
import unittest
import subprocess
import git

import mock
from hubsync import sync, github, workspace, config as hs_conifg


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
        self.base_url = u'base'
        self.path = subprocess.check_output('mktemp -d',
                                            shell=True).splitlines()[0]
        self.path = self.path.decode()
        print("Running tests in {}".format(self.path))
        self.gh_api = github.Api(api_url=self.base_url, user_token='')
        self.ws = workspace.Workspace(self.path)
        self.config = hs_conifg.Config()
        self.config.glob.interactive = False
        self.config.glob.sync_user = False
        self.config.glob.fork_repos = False
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

    @mock.patch('git.Repo')
    @mock.patch('hubsync.github.Api.get')
    def test_org_one_repo_not_locally_get_synced(self, api_get, git_mock):
        """Test a user with a repo locally already synced makes no change"""
        org_name = 'sample_org'
        repo_name = 'sample_repo'
        api_get.side_effect = gb_api_mock({
            'user': defaultdict(str, {
                'login': 'user',
                'repos_url': 'user/repos_url'
            }),
            'orgs': [defaultdict(str, {
                'url': 'org_url'
            })],
            'org_url': defaultdict(str, {
                'login': org_name,
                'repos_url': 'repos_url'
            }),
            'repos_url': [defaultdict(str, {
                'url': 'repo_url'
            })],
            'repo_url': defaultdict(str, {
                'owner': {
                    'login': org_name
                },
                'name': repo_name
            })
        }, {})
        self._create_local_org(org_name)

        def create_repo(_, path):
            print("Mock creating git repo in {}".format(path))
            os.makedirs(path)
            git.Git(path)

        git_mock.clone_from.side_effect = create_repo

        self.assertEqual(['sample_org'], next(os.walk(self.path))[1])

        self.syncer.sync(self.ws, self.gh_api)

        self.assertEqual(['sample_org'], next(os.walk(self.path))[1])
        file_tree = os.walk(self.path)
        next(file_tree)
        org_tree = next(file_tree)

        # repo is present now
        self.assertEqual([repo_name], org_tree[1])

    @mock.patch('hubsync.github.Api.get')
    def test_clone_user_repos_no_changes(self, api_get):
        """Test pre and post commands are run"""
        self.config.glob.sync_user = True
        user_name = 'user'
        api_get.side_effect = gb_api_mock({
            'user': defaultdict(str, {
                'login': user_name,
                'repos_url': 'user/repos_url'
            }),
            'orgs': [],
            'repos_url': []
        }, {})
        self._create_local_org(user_name)

        self.assertEqual([user_name], next(os.walk(self.path))[1])

        self.syncer.sync(self.ws, self.gh_api)

        self.assertEqual([user_name], next(os.walk(self.path))[1])

    @mock.patch('hubsync.github.Api.get')
    def test_clone_user_repo_create_folder(self, api_get):
        """Test pre and post commands are run"""
        self.config.glob.sync_user = True
        user_name = 'user'
        api_get.side_effect = gb_api_mock({
            'user': defaultdict(str, {
                'login': user_name,
                'repos_url': 'user/repos_url'
            }),
            'orgs': [],
            'repos_url': []
        }, {})
        self.assertEqual([], next(os.walk(self.path))[1])

        self.syncer.sync(self.ws, self.gh_api)

        self.assertEqual([user_name], next(os.walk(self.path))[1])

    @mock.patch('hubsync.github.Api.get')
    def test_org_pre_post_executed(self, api_get):
        """Test pre and post commands are run"""
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
        self.config.org.pre = "touch test.pre"
        self.config.org.post = "mkdir test.post"
        self._create_local_org(org_name)

        self.assertEqual(['sample_org'], next(os.walk(self.path))[1])

        self.syncer.sync(self.ws, self.gh_api)

        file_tree = os.walk(self.path)
        next(file_tree)
        org_tree = next(file_tree)

        # one dir
        self.assertEqual(['test.post'], org_tree[1])
        # one file
        self.assertEqual(['test.pre'], org_tree[2])
