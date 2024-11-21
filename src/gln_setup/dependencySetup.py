from pathlib import Path
import platform
import shutil
import sys
from dataclasses import dataclass, field
from subprocess import run, CalledProcessError, PIPE, DEVNULL
import json
from warnings import warn
from typing import Optional, Protocol

class PackageManager(Protocol):

    name: str 

    @property
    def is_pm_installed(self) -> bool:
        return bool(shutil.which(self.name))

    #NOTE: if it can be installed then install_app should also install the package manager.
    def install_app(self, app_name: str) -> None:
        pass


class Dependency(Protocol):

    packageManagers: list[PackageManager] = field(default_factory = lambda: [AptGet(), Brew(), Pipx(), Conda()])
    name: str

    @property
    def is_installed(self) -> bool:
        return bool(shutil.which(self.name))

    def install(self) -> None:
        if self.is_installed:
            return
        for pm in self.packageManagers:
            try:
                pm.install_app(self.name)
                if self.is_installed:
                    return
            except (CalledProcessError, FileNotFoundError):
                pass
            

@dataclass
class Conda(PackageManager):
    name: str = "conda"
    env_name: str = "gln-managed"
    python_version: str = "3.12"

    @property
    def is_initialized(self) -> bool:
        bashrcText = Path("~/.bashrc").expanduser().read_text()
        return "# >>> conda initialize >>>" in bashrcText.splitlines()

    @property
    def is_env_installed(self) -> bool:
        return bool(
            self.env_path
        )
            
    @property
    def env_path(self) -> Optional[str]:
        envList = [
            e for e in json.loads(
                run(
                    [self.name, 'env', 'list', '--json'],
                    check=True,
                    capture_output=True,
                ).stdout
            )['envs'] if Path(e).name == self.env_name
        ]
        try:
            return envList[0]
        except IndexError:
            return None

    def install(self) -> None:
        if self.is_pm_installed:
            return
        downloadCmd = ['wget', "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh", "-O", "~/miniconda3/miniconda.sh"] if platform.system().lower() == "linux" else ["curl", "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh", "-o", "~/miniconda3/miniconda.sh"]
        Path("~/miniconda3").expanduser().mkdir(parents=True, exist_ok=True)
        run(
            downloadCmd,
            check=True,
        )
        run(
            ["bash", "~/miniconda3/miniconda.sh", "-b", "-u", "-p,", "~/miniconda3",],
            check=True,
        )
        Path("~/miniconda3/miniconda.sh").expanduser().unlink(missing_ok=True)
        #warn("conda installed. You must reopen your terminal or run `source ~/miniconda3/bin/activate` from the shell to continue")
        # I think because each subprocess is a new shell this is ok?
        self.init()

    def init(self) -> None:
        run(
            [self.name, 'init'],
            check=True,
        )

    def install_env(self) -> None:
        if self.is_env_installed:
            return
        run(
            [self.name, 'create', '-n', self.env_name, "python=" + self.python_version],
            check=True,
        )

    def add_env_to_PATH(self) -> None: 
        bashrcFile = Path("~/.bashrc").expanduser()
        bashrcText = Path("~/.bashrc").expanduser().read_text()
        line = "export PATH=" + self.env_path + "/bin:$PATH"
        if line not in bashrcText.splitlines(keepends=True):
            bashrcText += "\n# >>> added by gln-setup\n" + line + "\n"
            bashrcFile.write_text(bashrcText)
        os.environ["PATH"] = f"{self.env_path}{os.pathsep}{os.environ['PATH']}" #changes path now

    def install_app(self, app_name: str) -> None:
        self.install()
        self.install_env()
        run(
            [self.name, "install", "-c", "conda-forge", "-y", "-n", self.env_name, app_name],
            check=True,
        )
        if not bool(shutil.which(app_name)):
            self.add_env_to_PATH()
            if not bool(shutil.which(app_name)):
                raise FileNotFoundError(f"{app_name} was not properly installed by conda.")

class AptGet(PackageManager):
    name: str = "apt-get"
    
    def install_app(self, app_name: str) -> None:
        run(
            ['sudo', self.name, 'install', '-y', app_name],
            check=True,
        )


class Brew(PackageManager):
    name: str = "brew"

    def install_app(self, app_name: str) -> None:
        run(
            [self.name, 'install', app_name],
            check=True,
        )

@dataclass
class Pipx(PackageManager, Dependency):
    name: str = "pipx"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [Conda(), AptGet(), Brew()])

    def install(self) -> None:
        if self.is_installed: return
        super().install()
        self.ensurepath()

    def ensurepath(self) -> None:
        run(
            [self.name, 'ensurepath'],
            check=True,
        )

    def install_app(self, app_name) -> None:
        run(
            [self.name, 'install', '--python', sys.executable, app_name],
            check=True,
        )

@dataclass
class Uv(PackageManager, Dependency):
    name: str = "uv"
    packageManagers: list[PackageManager] = field(default_factory = list)
    python_version: str = "3.12"

    def install(self) -> None:
        if self.is_installed:
            return
        with urllib.request.urlopen("https://astral.sh/uv/install.sh") as response:
            script_content = response.read().decode("utf-8")
        run(["sh"], input=script_content, text=True, check=True)

    def install_app(self, app_name) -> None:
        self.install()
        run(
            [self.name, 'tool', 'install', '--python', python_version, app_name],
            check=true
        )

        
@dataclass
class P7zip(Dependency):
    name: str = "p7zip"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [AptGet(), Brew(), Conda()])

@dataclass
class Git(Dependency):
    name: str = "git"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [AptGet(), Brew(), Conda()])

@dataclass
class GitAnnex(Dependency):
    name: str = "git-annex"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [AptGet(), Brew(), Conda()])

@dataclass
class Rclone(Dependency):
    name: str = "rclone"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [AptGet(), Brew(), Conda()])

@dataclass
class GitAnnexRemoteRclone(Dependency):
    name: str = "git-annex-remote-rclone"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [AptGet(), Brew(), Conda()])

@dataclass
class GitHubCli(Dependency):
    name: str = "gh"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [AptGet(), Brew(), Conda()])

    def install(self):
        if AptGet().is_pm_installed:
            run(
                ["sudo", "mkdir", "-p", "-m", "755", "/etc/apt/keyrings"],
                check=True,
            )
            wget_proc = run(
                ["wget", "-qO-", "https://cli.github.com/packages/githubcli-archive-keyring.gpg"],
                check=True,
                stdout=PIPE,
            )
            run(
                ["sudo", "tee", "/etc/apt/keyrings/githubcli-archive-keyring.gpg"],
                input = wget_proc.stdout,
                stdout = DEVNULL,
                check=True,
            )
            run(
                ["sudo", "chmod", "go+r", "/etc/apt/keyrings/githubcli-archive-keyring.gpg",],
                check=True
            )
            architecture = run(
                ["dpkg", "--print-architecture"],
                stdout=PIPE,
                text=True,
                check=True
            ).stdout.strip()
            echo_str = f'deb [arch={architecture} signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main'
            run(
                ["sudo", "tee", "/etc/apt/sources.list.d/github-cli.list"],
                input=echo_str,
                stdout=DEVNULL,
                text=True,
                check=True,
            )
            run(
                ["sudo", "apt", "update"],
                check=True,
            )
        super().install()

@dataclass
class Datalad(Dependency):
    name: str = "datalad"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [Uv(), Pipx(), Conda(), AptGet(), Brew()])

@dataclass
class Wget(Dependency):
    name: str = "wget"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [AptGet(), Brew()])

@dataclass
class Pdm(Dependency):
    name: str = "pdm"
    packageManagers: list[PackageManager] = field(default_factory = lambda: [Uv(), Pipx(),])

def install_dependencies(dependencies: list[Dependency] = [P7zip(), Git(), GitAnnex(), Rclone(), GitAnnexRemoteRclone(), Wget(), GitHubCli(), Uv(),]) -> None:
    for dependency in dependencies:
        dependency.install()

