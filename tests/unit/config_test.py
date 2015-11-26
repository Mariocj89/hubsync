import unittest

import mock
from six.moves import configparser

from hubsync import config


class ConfigTestCase(unittest.TestCase):
    """Basic tests for building the config

    The main objective of the test is to see that it builds, that is why there
    are not that many assertions
    """
    @mock.patch('six.moves.configparser.ConfigParser.read')
    def test_create_from_empty_ini(self, read_mock):
        read_mock.return_value = None
        conf = config.Config.from_ini_file('fake')
        self.assertIsNone(conf.github.token)

    @mock.patch('hubsync.config._get_config_parser')
    def test_create_from_ini_with_sections(self, parser_mock):
        parser = configparser.ConfigParser()
        parser.add_section('github')
        parser_mock.return_value = parser
        conf = config.Config.from_ini_file('fake')
        self.assertIsNone(conf.github.token)

    @mock.patch('hubsync.config._get_config_parser')
    def test_create_from_ini_with_values(self, parser_mock):
        parser = configparser.ConfigParser()
        parser.add_section('github')
        parser.set('github', 'token', 'value')
        parser_mock.return_value = parser
        conf = config.Config.from_ini_file('fake')
        self.assertEqual('value', conf.github.token)

    def test_create_from_ini_with_invalid_value(self):
        self.assertRaises(AssertionError,
                          lambda: config.Config(org={'a': 1}))

if __name__ == '__main__':
    unittest.main()
