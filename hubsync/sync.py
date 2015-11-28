"""File wrapping sync related functions,

You will see that this files uses the workspace repo/org and the github repo/org
 together with the raw Api of git for example. We are aware this is not the best
 design and ideally all git calls should be hidden within the workspace module
 but we chose to be pragmatic for the moment as doing so will raise the current
 complexity of the workspace module in a way that is not justifiable for the
 moment. Lets not make best the enemy of better :). You are though welcome to
 come up with a better solution.
"""
from contextlib import contextmanager
import logging
import shutil
import os
import subprocess

import git

from . import workspace


LOG = logging.getLogger('hubsync.sync')


@contextmanager
def git_wrap(git_item):
    cw = git_item.config_writer
    yield cw
    cw.release()


def zip_pairs(xs, ys, key=lambda x: x):
    """Generate pairs that match a cmp function"""
    xs = list(reversed(sorted(xs, key=key)))
    ys = list(reversed(sorted(ys, key=key)))

    while xs or ys:
        if xs and not ys:
            yield xs.pop(), None
        elif ys and not xs:
            yield None, ys.pop()
        elif key(xs[-1]) == key(ys[-1]):
            yield xs.pop(), ys.pop()
        elif key(xs[-1]) < key(ys[-1]):
            yield xs.pop(), None
        else:
            yield None, ys.pop()


@contextmanager
def cd(path):
    """Context manager that cds to a path"""
    saved_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(saved_path)


def yesno_as_boolean(yesno_string):
    """converts text containing yes or no to a bool"""
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    return valid[yesno_string.lower()]


def input_yesno(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    From ActiveState recipe 577058
    """
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        print(question + prompt),
        choice = raw_input()
        if default is not None and choice == '':
            return yesno_as_boolean(default)
        else:
            try:
                return yesno_as_boolean(choice)
            except KeyError:
                print("Please respond with 'yes' or 'no' (or 'y' or 'n').")


def run_commands(commands):
    """Runs a bash command in the current workspace"""
    if commands:
        subprocess.call(commands, shell=True)


class SyncHelper(object):
    """Class that wraps the synchronization of objects"""

    def __init__(self, api, config):
        """ Initializes the sync helper

        :type api: hubsync.github.api
        :type config: hubsync.config.Config
        :param api: github helper
        :param config: parsed global configuration
        """
        self.api = api
        self.config = config

    def yesno(self, question, default):
        """Using the local config, prompts the user if necesary"""
        if self.config.glob.interactive:
            return input_yesno(question, default)
        else:
            return yesno_as_boolean(default)

    def sync(self, local_workspace, github_api):
        """Syncs using a workspace and a github api
        :param local_workspace:  local workspace object
        :type local_workspace: hubsync.workspace.Workspace
        :param github_api: remote organizations
        :type github_api: hubsync.github.Api
        """
        LOG.debug("Syncing organizations. workspace {} with github {}"
                  .format(local_workspace, github_api))
        for local_org, github_org in zip_pairs(
                local_workspace.organizations, github_api.organizations,
                lambda x: x.name):

            if not github_org:
                print("Found organization {} locally but not in github."
                      .format(local_org.name))
                if self.yesno("Delete locally?", "no"):
                    shutil.rmtree(local_org.path)
                continue

            if not local_org:
                print("Found organization {} in github but not locally."
                      .format(github_org.name))
                if self.yesno("Clone locally?", "yes"):
                    os.makedirs(os.path.join(local_workspace.path,
                                             github_org.name))
                    local_org = workspace.Organization(github_org.name,
                                                       local_workspace.path)
                else:
                    continue

            with cd(local_org.path):
                run_commands(self.config.org.pre)
                self.sync_org(local_org, github_org)
                run_commands(self.config.org.post)

    def sync_org(self, local_org, github_origin):
        """Syncs the org across the workspace and the origin

        :param local_org: local workspace of the org
        :param github_origin: github storage of the org
        """
        LOG.info("Syncing organization {}".format(local_org.name))
        for local_repo, github_repo in zip_pairs(
                local_org.repos, github_origin.repos,
                lambda x, y: cmp(x.name, y.name)):
            if not github_repo:
                print("Found repo {} locally but not in github."
                      .format(local_repo.name))
                if self.yesno("Delete locally?", "no"):
                    shutil.rmtree(local_repo.path)
                continue

            if not local_repo:
                print("Found repo {} in github but not locally."
                      .format(github_repo.name))
                if self.yesno("Clone locally?", "yes"):
                    git.Git().clone(github_repo.url)
                    local_repo = workspace.Repo(github_repo.name,
                                                local_org.path)
                else:
                    continue

            with cd(local_repo.path):
                run_commands(self.config.repo.pre)
                self.sync_repo(local_repo, github_repo)
                run_commands(self.config.repo.post)

    def sync_repo(self, local_repo, github_repo):
        """Syncs the repo with github

        It syncs remotes and branches
        """
        LOG.info("Syncing repo {}".format(local_repo.name))

        def sync_remotes():
            """Sets up the remotes

            - origin: origin of the repo
            - upstream: origin with push options
            - fork: user's fork of the repo
            """
            LOG.debug("Syncing remotes")
            # set origin
            try:
                origin = local_repo.git.remote('origin')
            except ValueError:
                origin = local_repo.git.create_remote('origin', github_repo.url)
            with git_wrap(origin) as writer:
                writer.set('pushurl', 'nopush')
            origin.fetch()

            # set upstream
            try:
                upstream = local_repo.git.remote('upstream')
            except ValueError:
                upstream = local_repo.git.create_remote('upstream',
                                                        github_repo.url)
            upstream.fetch()

            # set fork
            # TODO

        def sync_branches():
            """Sincs/update/clean local/fork branches"""
            LOG.debug("Syncing branches")
            # clean merged branches
            for branch in local_repo.git.heads:
                commits_ahead = list(local_repo.git.iter_commits(
                    "origin/master..{}".format(branch.name)))
                commits_behind = list(local_repo.git.iter_commits(
                    "{}..origin/master".format(branch.name)))
                if not commits_ahead and commits_behind:
                    print("Found stale branch {} locally.".format(branch.name))
                    if self.yesno("Delete locally?", "yes"):
                        local_repo.git.delete_head(branch.name)

        def sync_fork():
            """Syncs and clears the fork (if any)"""
            pass

        sync_remotes()
        sync_branches()
        sync_fork()
