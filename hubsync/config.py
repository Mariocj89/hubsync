"""Stores the config related classes/functions"""
import os
from six.moves import configparser


FALSY_VALUES = ['False', 'false', 'no']


def _parse_ini_section(config, section, attributes):
    """Extracts a section from a config parser

    Given a Config parser, a section and a list of attributes extracts them as a
    dictionary, the attributes that are not present wont appear in the dict
    :type config: ConfigParser.ConfigParser
    :type section: str
    :type attributes: tuple
    :param config: Python Config parser
    :param section: section to extract
    :param attributes: attributes within the section to extract
    :return: dictionary with the extracted data
    """
    ret = {}
    for attr in attributes:
        try:
            value = config.get(section, attr)
            if value in FALSY_VALUES:
                ret[attr] = False
            else:
                ret[attr] = value
        except configparser.NoOptionError:
            continue
        except configparser.NoSectionError:
            break
    return ret


def _get_config_parser(path):
    """Given a path, gets a config parser"""
    ret = configparser.ConfigParser()
    ret.read(os.path.expanduser(path))
    return ret


class Config(object):
    """Structured config for the application"""

    @staticmethod
    def from_ini_file(path):
        """Creates a config given the path to a ini file

        :return Config
        """
        parser = _get_config_parser(path)
        github_attrs = ('token', 'api_url')
        ws_attrs = ('path',)
        org_attrs = ('pre', 'post')
        repo_attrs = ('path', 'post')
        global_attrs = ('interactive', 'sync_user', 'fork_repos',
                        'case_sensitive')
        result = {
            'github': _parse_ini_section(parser, 'github', github_attrs),
            'workspace': _parse_ini_section(parser, 'workspace', ws_attrs),
            'org': _parse_ini_section(parser, 'org', org_attrs),
            'repo': _parse_ini_section(parser, 'repo', repo_attrs),
            'glob': _parse_ini_section(parser, 'global', global_attrs),
        }
        return Config(**result)

    def __init__(self, **kwargs):
        self.github = self.Github(**kwargs.get('github', {}))
        self.workspace = self.Workspace(**kwargs.get('workspace', {}))
        self.org = self.Organization(**kwargs.get('org', {}))
        self.repo = self.Repository(**kwargs.get('repo', {}))
        self.glob = self.Global(**kwargs.get('glob', {}))

    class Global(object):
        """Hubsync global config"""
        def __init__(self, **kwargs):
            self.interactive = kwargs.pop('interactive', True)
            self.sync_user = kwargs.pop('sync_user', True)
            self.fork_repos = kwargs.pop('fork_repos', False)
            self.case_sensitive = kwargs.pop('case_sensitive', True)
            assert not kwargs, "Unknown config: {}".format(kwargs.keys())

    class Github(object):
        """Github global config"""
        def __init__(self, **kwargs):
            self.api_url = kwargs.pop('api_url', 'https://api.github.com')
            self.token = kwargs.pop('token', None)
            assert not kwargs, "Unknown config: {}".format(kwargs.keys())

    class Workspace(object):
        """Workspace config"""
        def __init__(self, **kwargs):
            self.path = kwargs.pop('path', os.getcwd())
            assert not kwargs, "Unknown config: {}".format(kwargs.keys())

    class Organization(object):
        """Org config"""
        def __init__(self, **kwargs):
            self.pre = kwargs.pop('pre', "")
            self.post = kwargs.pop('post', "")
            assert not kwargs, "Unknown config: {}".format(kwargs.keys())

    class Repository(object):
        """Repo config"""
        def __init__(self, **kwargs):
            self.pre = kwargs.pop('pre', "")
            self.post = kwargs.pop('post', "")
            assert not kwargs, "Unknown config: {}".format(kwargs.keys())
