.. image:: https://travis-ci.org/Mariocj89/hubsync.svg?branch=master
    :target: https://travis-ci.org/Mariocj89/hubsync

.. image:: https://coveralls.io/repos/Mariocj89/hubsync/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/Mariocj89/hubsync?branch=master

.. image:: https://badge.fury.io/py/hubsync.svg
    :target: https://badge.fury.io/py/hubsync


Objective
#########
This scripts allows you to keep the organization you work in sync with your local workspace.

The main objective is to centralize your workflow and integrate all the syncronization and cleaning activities you perform daily related to your local file structure and your github organization

How it works
############
The script mainly relies on your config file ".hubsyncrc" to run all the commands and to customize how to sync your github projects locally

Config File
###########
The hubsync config file contains all the configuration that hubsync requires and it is the main way to customize the script.

It should be located in in your home with the name .hubsyncrc (*~/.hubsyncrc*)

An example of its minimun content is:

|   [github]
|   token: XXXXXXX
|   [workspace]
|   path: ~/workspace/test
|

See `this guide <https://help.github.com/articles/creating-an-access-token-for-command-line-use/>`_ about how to generate a token


Note: Work ongoing
