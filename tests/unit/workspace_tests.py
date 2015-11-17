"""Tests for hubsync.workspace module"""
import unittest
import git
import mock
from hubsync.workspace import Organization, InvalidPath, Workspace, Repo


class WorkspaceTestCase(unittest.TestCase):
    def setUp(self):
        self.path = "/the/org/path/"
        self.ws = Workspace(self.path)

    def test_ws_repr(self):
        repr(self.ws)

    @mock.patch("hubsync.workspace.get_sub_folders")
    def test_no_subfolder_returns_no_org(self, mock_subfolders):
        mock_subfolders.return_value = []
        self.assertEqual(0, len(self.ws.organizations))

    @mock.patch("hubsync.workspace.get_sub_folders")
    def test_workspace_invalid_path_raises(self, mock_subfolders):
        mock_subfolders.side_effect = StopIteration
        self.assertRaises(InvalidPath, lambda: self.ws.organizations)


class OrgTestCase(unittest.TestCase):
    def setUp(self):
        self.org_name = "org_name"
        self.org_path = "/the/org/path/"
        self.org = Organization(self.org_name, self.org_path)

    def test_create_org_appends_path(self):
        self.assertEqual(self.org_path + self.org_name, self.org.path)

    def test_create_org_fixes_incorrect_path(self):
        org_path = "/the/org/path"  # Note the missing slash
        org = Organization(self.org_name, org_path)
        self.assertEqual(self.org.path, org.path)

    def test_org_repr(self):
        repr(self.org)

    @mock.patch("hubsync.workspace.get_sub_folders")
    def test_org_with_no_subfolders(self, mock_subfolders):
        mock_subfolders.return_value = []
        self.assertEqual(0, len(self.org.repos))

    @mock.patch("hubsync.workspace.get_sub_folders")
    def test_org_for_invalid_path(self, mock_subfolders):
        mock_subfolders.side_effect = StopIteration
        self.assertRaises(InvalidPath, lambda: self.org.repos)

    @mock.patch("hubsync.workspace.get_sub_folders")
    @mock.patch("git.Repo")
    def test_org_with_a_subfolders_but_not_a_repo_raises(self, mock_git, mock_subfolders):
        mock_git.side_effect = git.exc.InvalidGitRepositoryError
        mock_subfolders.return_value = ["secret_folder_without_repo"]
        self.assertRaises(InvalidPath, lambda: self.org.repos)


class RepoTestCase(unittest.TestCase):
    def setUp(self):
        self.__git_repo = git.Repo
        git.Repo = mock.MagicMock(git.Repo)
        self.name = "org_name"
        self.path = "/the/repo/path/"
        self.repo = Repo(self.name, self.path)

    def tearDown(self):
        git.Repo = self.__git_repo

    def test_create_repo_appends_path(self):
        self.assertEqual(self.path + self.name, self.repo.path)

    @mock.patch("git.Repo")
    def test_create_repo_fixes_incorrect_path(self, mock_git):
        mock_git.return_value = None
        path = "/the/repo/path"  # Note the missing slash
        repo = Repo(self.name, path)
        self.assertEqual(self.repo.path, repo.path)

    def test_repo_repr(self):
        repr(self.repo)


if __name__ == '__main__':
    unittest.main()
