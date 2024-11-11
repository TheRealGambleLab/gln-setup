import unittest
from unittest.mock import patch
from subprocess import run

from typer.testing import CliRunner

from gln_setup.dependencySetup import is_installed

class TestGitConfig(unittest.TestCase):

    @patch("shutil.which")
    def test_is_installed_true(self, mock_which):
        mock_which.return_value = "/usr/bin/git"
        result = is_installed('git')
        mock_which.assert_called_with('git')
        self.assertTrue(result)

    @patch("shutil.which")
    def test_is_installed_false(self, mock_which):
        mock_which.return_value = None
        result = is_installed("notthere")
        mock_which.assert_called_with("notthere")
        self.assertFalse(result)
        


