from pathlib import Path
from subprocess import run, CalledProcessError
from typing import Optional, ClassVar
from warnings import warn
from dataclasses import dataclass

from . import sshconfig

@dataclass
class SSHkey:
    name: Optional[str] = None
    comment: str = ""
    protocol: str = "ed25519"
    byte_length: int = 4096 #only used for rsa
    force: bool = False
    key_path: Optional[Path] = None

    def __post_init__(self):
        #set key_path
        if self.key_path is None and self.name is None:
            raise ValueError("Either key_path or name must not be none")
        if self.name is None:
            self.name = "_".join(self.key_path.name.split("_")[2:])
        elif self.key_path is None:
            self.key_path = Path(f"~/.ssh/id_{self.protocol}_{name}")
        self.key_path = self.key_path.expanduser()
        
    def create(self):
        if self.key_path.exists() and not self.force:
            raise ValueError(f"{key_path} aleady exists and force not set.")
            return
        cmd = ['ssh-keygen', '-t', self.protocol, '-C', self.comment, '-f', str(self.key_path)]
        if self.protocol == "rsa":
            cmd += ['-b', str(self.byte_length)]
        warn("Reminder: it is best to not set a passphrase (just push enter)")
        run(
            cmd,
            shell=True,
            check=True,
        )

    def send_to_server(self, target: str):
        if target == "git@github.com":
            self.sendKeytoGithub()
            return
        run(
            ["ssh-copy-id", "-i", str(self.key_path.with_suffix('.pub')), self.target,],
            shell=True,
            check=True,
        )

    def send_to_github(self):
        run(
            ["gh", "auth", "login", "-p", "ssh", "-h", "github.com", "-w"],
            shell=True,
            check=True,
        )
        run(
            ["gh", "ssh-key", "add", "-t", self.name, self.key_path],
            shell=True,
            check=True,
        )

    def add_to_config(self, host: str, path: Path = Path("~/.ssh/config"), **hostOptions: dict[str,str]):
        path = path.expanduser()
        config = sshconfig.load(path)
        section = config.get(host, Section())
        section['host'] = host
        for k,v in hostOptions:
            section[k] = v
        section['IdentityFile'] = self.key_path
        sshconfig.dump(config, path)

