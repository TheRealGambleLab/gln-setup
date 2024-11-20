from pathlib import Path
from subprocess import run, CalledProcessError
from typing import Optional, ClassVar
from warnings import warn
from dataclasses import dataclass

#from . import sshconfig
from sshconf import read_ssh_config, empty_ssh_config_file

@dataclass
class SSHkey:
    name: Optional[str] = None
    comment: str = ""
    protocol: str = "ed25519"
    byte_length: int = 4096 #only used for rsa
    force: bool = False
    key_path: Optional[Path] = None
    passphrase: str = ""

    def __post_init__(self):
        #set key_path
        if self.key_path is None and self.name is None:
            raise ValueError("Either key_path or name must not be none")
        if self.name is None:
            self.name = "_".join(self.key_path.name.split("_")[2:])
        elif self.key_path is None:
            self.key_path = Path(f"~/.ssh/id_{self.protocol}_{self.name}")
        self.key_path = self.key_path.expanduser()
        
    def create(self):
        if self.key_path.exists() and not self.force:
            raise ValueError(f"{self.key_path} aleady exists and force not set.")
        cmd = ['ssh-keygen', '-q', '-t', self.protocol, '-C', self.comment, '-f', str(self.key_path), '-N', self.passphrase]
        print(" ".join(cmd))
        if self.protocol == "rsa":
            cmd += ['-b', str(self.byte_length)]
        #warn("Reminder: it is best to not set a passphrase (just push enter)")
        run(
            cmd,
            check=True,
        )

    def send_to_server(self, target: str):
        if target == "git@github.com":
            self.send_to_github()
            return
        run(
            ["ssh-copy-id", "-i", str(self.key_path.with_suffix('.pub')), target,],
            check=True,
        )

    def send_to_github(self):
        print("follow the instructions carefully to load your new ssh-key to github...")
        run(
            ["gh", "auth", "login", "-p", "ssh", "-h", "github.com", "-w"],
            check=True,
        )

    def add_to_config(self, host: str, path: Path = Path("~/.ssh/config"), **hostOptions: dict[str,str]):
        path = path.expanduser()
        options = dict(hostOptions)
        if "@" in host:
            options["User"], options["HostName"] = host.split("@")
        else:
            options["HostName"] = host
        options["IdentityFile"] = str(self.key_path)
        config = read_ssh_config(path) if path.exists() else empty_ssh_config_file()
        func = config.set if options["HostName"] in config.hosts() else config.add
        func(options["HostName"], **options)
        config.write(path)
