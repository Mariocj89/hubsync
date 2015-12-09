"""Tests using captured github req/res"""

import os
import shutil
import unittest
import subprocess
import pickle
import git

import mock
from hubsync import sync, github, workspace, config as hs_conifg

DIR = os.path.dirname(os.path.realpath(__file__))


def fake_clone(_, folder):
    os.makedirs(folder)
    git.Repo.init(folder)


class RecordedGithubTestCase(unittest.TestCase):
    """Sanity tests using recorded requests and responses and a temp folder"""

    def _create_local_org(self, name):
        """Creates a folder that represents an org locally"""
        os.makedirs(os.path.join(self.path, name))

    def setUp(self):
        self.base_url = u'https://api.github.com/'
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

        with open(os.path.join(DIR, "gh_responses.pickle")) as pickled_file:
            responses = pickle.load(pickled_file)

        def faked_req(key):
            return responses[key]
        self.gh_api.get = faked_req
        self.gh_api.post = faked_req

        self.syncer = sync.SyncHelper(self.gh_api, self.config)

        self.clone_patcher = mock.patch('hubsync.sync.git.Repo.clone_from')
        self.clone_patcher.start().side_effect = fake_clone

        self.fetch_patcher = mock.patch('hubsync.workspace.git')
        self.fetch_patcher.start()

    def tearDown(self):
        self.clone_patcher.stop()
        self.fetch_patcher.stop()
        shutil.rmtree(self.path)

    def test_sanity(self):
        """Just checks this runs"""
        self.syncer.sync(self.ws, self.gh_api)
