.. image:: https://travis-ci.org/Mariocj89/hubsync.svg?branch=master
    :target: https://travis-ci.org/Mariocj89/hubsync

.. image:: https://coveralls.io/repos/Mariocj89/hubsync/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/Mariocj89/hubsync?branch=master

.. image:: https://badge.fury.io/py/hubsync.svg
    :target: https://badge.fury.io/py/hubsync


Hubsync
#########
This script allows you to keep the organization you work in sync with your local workspace.

The main objective is to centralize your workflow and integrate all the syncronization and cleaning activities you perform daily related to your local file structure and your github organization

You can get it with pip by running "pip install hubsync".

Want to contribute? Have a look to our `guidelines <https://github.com/Mariocj89/hubsync/blob/master/CONTRIBUTING.md>`_

How it works
############
The script mainly relies on your config file ".hubsyncrc" to run all the commands and to customize how to sync your github projects locally

Based on the options within the config files it will sync locally all the organizations you belong too as folders and will create git repositories within them for each github repostory within the org.

Moreover, within your local repostiories it will delete all stale branches and set three remotes:

- origin: url of the main repo (push is disabled)
- upstream: url of the main repo (both pull and push)
- fork: url of a fork of the repo within your user space

Note that if you are the owner of the repo only origin will be set

Config File
###########
The hubsync config file contains all the configuration that hubsync requires and it is the main way to customize the script.

It should be located in in your home with the name .hubsyncrc (*~/.hubsyncrc*)

As your hubsyncrc file includes your github token, remember to make it not readable to any user but yourself.

chmod 600 ~/.hubsyncrc


Example
*******
An example of its minimun content (mandatory params) is:

|   [github]
|   token: XXXXXXX
|   [workspace]
|   path: ~/workspace/test
|

See `this guide <https://help.github.com/articles/creating-an-access-token-for-command-line-use/>`_ about how to generate a token

All options
***********
Below you can find all config options with an explanation and the default value

global

- interactive: Set to false to never get prompted. Hubsync will use defaults always. (True)
- sync_user: Sync user repositories locally? (True)
- fork_repos: Create a fork of all organization repos in your user space. (False)
- case_sensitive: Whether to considering the case when matching github repos and your local folders. (True)

github

- api_url: base url of the github api, use this if you want to use hubsync in a github enterprise instance. (https://api.github.com)
- token: github api token. Never share this with anyone.

org

- pre: shell command to run before syncing an organization (None)
- post shell command to run before syncing an organization (None)

repo

- pre: shell command to run before syncing an repo (None)
- post shell command to run before syncing an repo (None)



Note: Work ongoing
