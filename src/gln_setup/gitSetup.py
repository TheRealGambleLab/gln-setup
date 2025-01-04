from dataclasses import dataclass, field
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_output, run
from typing import Optional
from warnings import warn


@dataclass
class GitInfo:
    installed: bool = field(init=False)
    filename: Optional[Path] = None
    prefixCmd: list[str] = field(init=False)

    def __post_init__(self):
        self.__check_install()
        self.__set_prefixCmd()

    def __set_prefixCmd(self) -> None:
        self.prefixCmd = ["git", "config"] + (
            ["--global"]
            if self.filename is None
            else ["--file", self.filename]
        )

    def __check_install(self) -> None:
        try:
            check_output(["git", "--version"], stderr=STDOUT)
            self.installed = True
        except (CalledProcessError, FileNotFoundError):
            self.installed = False

    @property
    def name(self) -> Optional[str]:
        try:
            return run(
                self.prefixCmd + ["user.name"],
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip()
        except CalledProcessError:
            return None

    def set_name(self, value: str, force: bool = False) -> None:
        if self.name is not None and not force:
            warn(
                "user.name already set. "
                "No changes made. Use 'force' to override."
            )
            return
        run(self.prefixCmd + ["user.name", value], check=True)

    @property
    def email(self) -> Optional[str]:
        try:
            return run(
                self.prefixCmd + ["user.email"],
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip()
        except CalledProcessError:
            return None

    def set_email(self, value: str, force: bool = False) -> None:
        if self.email is not None and not force:
            warn(
                "user.email already set. No changes made. "
                "Use 'force' to override."
            )
            return
        run(self.prefixCmd + ["user.email", value], check=True)
