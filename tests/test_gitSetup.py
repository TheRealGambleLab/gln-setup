import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile
from subprocess import run
from typing import IO

from typer.testing import CliRunner

from gln_setup.cli import app
from gln_setup.gitSetup import GitInfo


class TestGitConfig(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.name = 'John Doe'
        self.email = 'john.doe@whoknows.edu'
        self.new_name = "Peter Griffen"
        self.new_email = "peter.griffen@familyguy.edu"

    def addInfoToFile(self, f: IO[str]):
        run(
            ['git', 'config', '--file', f.name, 'user.name', self.name],
            check = True
        )
        run(
            ['git', 'config', '--file', f.name, 'user.email', self.email],
            check = True
        )
        
    def testGitInfoRetreival(self):
        with NamedTemporaryFile() as f:
            self.addInfoToFile(f)
            gi = GitInfo(Path(f.name))
            self.assertEqual(str(gi.filename), f.name)
            self.assertEqual(gi.name, self.name)
            self.assertEqual(gi.email, self.email)

    def testGitInfoSettingForce(self):
        with NamedTemporaryFile() as f:
            self.addInfoToFile(f)
            gi = GitInfo(Path(f.name))
            gi.set_name(self.new_name)
            self.assertEqual(self.name, gi.name)
            gi.set_name(self.new_name, force=True)
            self.assertEqual(self.new_name, gi.name)
            gi.set_email(self.new_email)
            self.assertEqual(self.email, gi.email)
            gi.set_email(self.new_email, force=True)
            self.assertEqual(self.new_email, gi.email)

    def testGitInfoCli(self):
        with NamedTemporaryFile() as f:
            self.addInfoToFile(f)
            result = self.runner.invoke(app, ['git', '--name', self.new_name, '--email', self.new_email, "--file", f.name])
            self.assertEqual(result.exit_code, 0)
            gi = GitInfo(Path(f.name))
            self.assertEqual(self.name, gi.name)
            self.assertEqual(self.email, gi.email)
            result2 = self.runner.invoke(app, ['git', '--name', self.new_name, '--email', self.new_email, "--force", "--file", f.name])
            self.assertEqual(result2.exit_code, 0)
            self.assertEqual(self.new_name, gi.name)
            self.assertEqual(self.new_email, gi.email)
            
        

