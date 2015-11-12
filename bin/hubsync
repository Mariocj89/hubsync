#!/usr/bin/env python

import os
import logging
import argparse

from hubsync import github, workspace, sync

LOG = logging.getLogger('hubsync')
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Keeps your repos in sync!")
    parser.add_argument('--github_api_url', type=str,
                        default="https://api.github.com")
    parser.add_argument('--github_token', type=str, required=True)
    args = parser.parse_args()

    api_args = dict()
    api_args["api_url"] = args.github_api_url
    api_args["user_token"] = args.github_token
    github_api = github.Api(**api_args)
    local_workspace = workspace.Workspace(os.getcwd())

    sync_helper = sync.SyncHelper(github_api)
    sync_helper.sync_all(
        workspaces=local_workspace.organizations,
        github_organizations=github_api.organizations
    )


