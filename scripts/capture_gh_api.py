#!/usr/bin/env python
""""Script to capture github responses

It will scrap the whole github api and save the responses in an python file
"""
from __future__ import unicode_literals
import logging
import argparse
import pprint

from hubsync import github, config as hubsync_config


LOG = logging.getLogger('hubsync.scrapper')
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler())


class Scrapper(object):
    def __init__(self, api, max_depth):
        """

        :type api: hubsync.github.Api
        :param max_depth:
        :return:
        """
        self.api = api
        self.max_depth = max_depth
        self.res = dict()

    def scrap(self, target, recursion=0):
        """Scraps an target"""
        if recursion > self.max_depth:
            return self.res

        LOG.debug("[{}] Scrapping {}".format(recursion, target))
        if isinstance(target, dict):
            for new_url in target.values():
                self.scrap(new_url, recursion)
        if isinstance(target, (list, tuple)):
            for new_url in target:
                self.scrap(new_url, recursion)
        if isinstance(target, basestring):
            try:
                target = target[:target.index("{")]
            except ValueError:
                pass
            if target not in self.res and self.api.base_url in target:
                LOG.info("[{}] Parsed {}".format(recursion, target))
                try:
                    data = self.api.get(target)
                except ValueError:
                    data = "NOT JSON"
                self.res[target] = data
                self.scrap(data, recursion + 1)

        return self.res


def main():
    config = hubsync_config.Config.from_ini_file('~/.hubsyncrc')
    parser = argparse.ArgumentParser(
        description="Testing tool to get all github responses",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--github_api_url', type=str,
                        required=not config.github.api_url,
                        default=config.github.api_url,
                        help="Base URL for the github instance.")
    parser.add_argument('--github_token', type=str,
                        required=not config.github.token,
                        default=config.github.token,
                        help="Private user token to get access to github")
    parser.add_argument('--logging', choices=['INFO', 'DEBUG', 'ERROR'],
                        required=False, default='INFO', type=str,
                        help="Logging level of the script")
    parser.add_argument('--output_file', type=str, required=False,
                        default='gh_responses.py',
                        help="Out file to save the result")
    parser.add_argument('--max_depth', type=int, required=False, default=3,
                        help="How deep to go in the scrapping of urls")
    args = parser.parse_args()

    LOG.setLevel(args.logging)

    api_args = {
        "api_url": args.github_api_url,
        "user_token": args.github_token
    }

    api = github.Api(**api_args)
    res = Scrapper(api, args.max_depth).scrap(api.base_url + '/user')
    with open(args.output_file, 'w') as output:
        pprint.pprint(res, output)


if __name__ == "__main__":
    main()
