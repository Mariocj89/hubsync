"""Module with the same name tests"""

import unittest

import mock

from hubsync.github import Api, Organization, Repo


class ApiTestCase(unittest.TestCase):
    """Tests for the gb api"""

    def setUp(self):
        self.api = Api('sample_url', 'awesome token')

    @mock.patch('hubsync.github.requests')
    def test_token_is_sent_in_header(self, requests_mock):
        requests_mock.get.return_value = mock.MagicMock()
        self.api.get('test')
        headers = requests_mock.get.call_args[1]['headers']
        self.assertTrue('Authorization' in headers)
        self.assertTrue('awesome token' in headers['Authorization'])

    def test_get_organizations_none_returned(self):
        self.api.get = mock.Mock(return_value=[])
        self.assertEqual(len(self.api.organizations), 0)

    def test_get_organizations_one_returned(self):
        def call_api(url):
            if 'user/org' in url:
                return [{'url': 'repo_url'}]
            elif 'repo_url' in url:
                return {
                    'login': 'sample_repo',
                    'description': 'description!',
                    'repos_url': 'http://localhost/repos'
                }
            else:
                raise ValueError()

        self.api.get = mock.MagicMock(side_effect=call_api)
        self.assertEqual(len(self.api.organizations), 1)

    def test_organizations_two_returned(self):
        def call_api(url):
            if 'user/org' in url:
                return [{'url': 'repo_url'}, {'url': 'repo_url'}]
            elif 'repo_url' in url:
                return {
                    'login': 'sample_repo',
                    'description': 'description!',
                    'repos_url': 'http://localhost/repos'
                }
            else:
                raise ValueError()

        self.api.get = mock.MagicMock(side_effect=call_api)
        self.assertEqual(len(self.api.organizations), 2)

    def test_create_organization(self):
        self.api.get = mock.MagicMock(return_value={
            'login': 'sample_org',
            'description': 'description!',
            'repos_url': 'http://localhost/repos'
        })
        org = Organization.from_url(self.api, 'the org url!')
        print(repr(org))
        self.assertEqual('sample_org', org.name)
        self.assertEqual('description!', org.description)

    def test_get_repos_from_org(self):
        def call_api(url):
            if 'org' in url:
                return {
                    'login': 'sample_org',
                    'description': 'description!',
                    'repos_url': 'repos'
                }
            elif 'repos' in url:
                return [{
                            'url': 'http://localhost/a_repo'
                        }]
            elif 'a_repo' in url:
                return {
                    'owner': {
                        "login": "the_user"
                    },
                    'name': 'sample_repo',
                    'description': 'description!',
                    'ssh_url': 'http://localhost/repos',
                    'forks_url': 'http://localhost/repos/forks'
                }
            else:
                raise ValueError()

        self.api.get = mock.MagicMock(side_effect=call_api)
        org = Organization.from_url(self.api, 'the org url!')
        self.assertEqual(len(org.repos), 1)

    @mock.patch('hubsync.github.Api.get')
    def test_get_forks_of_repo(self, requests_mock):
        requests_mock.return_value = [{
                                          "name": "fork_name",
                                          "description": "desc",
                                          "ssh_url": "clone_me"
                                      }]

        tested_repo = Repo(self.api, 'user', 'name', 'desc', 'the_url', 'forks')
        self.assertEqual(1, len(tested_repo.forks))


if __name__ == '__main__':
    unittest.main()
