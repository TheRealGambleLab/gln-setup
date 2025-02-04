from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Annotated, Optional

import typer

from .dependencySetup import install_dependencies
from .gitSetup import GitInfo
from .sshSetup import SSHkey

app = typer.Typer()


@app.callback()
def main(
    ctx: typer.Context,
    configPath: Annotated[
        Path,
        typer.Option(
            "-C", help="Path to a non-default config.toml file for the gln."),
    ] = Path(typer.get_app_dir("gln"), "config.toml"),
) -> None:
    """
    Plugin for the gln to automte system setup.
    """
    pass


@app.command()
def git(
    ctx: typer.Context,  # is this needed?
    name: Annotated[
        Optional[str],
        typer.Option(help="enter your first and last name (e.g. 'John Doe')"),
    ] = None,
    email: Annotated[
        Optional[str], typer.Option(help="enter your email address.")
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force/",
            "-f/",
        ),
    ] = False,
    file: Annotated[
        Optional[Path],
        typer.Option(hidden=True),
    ] = None,
) -> None:
    gi = GitInfo(file)
    if not gi.installed:
        raise RuntimeError("git was not found on system.")
    if name is not None:
        gi.set_name(name, force)
    if email is not None:
        gi.set_email(email, force)


@app.command()
def install_deps(
    ctx: typer.Context,  # is this needed?
) -> None:
    install_dependencies()


# TODO: Need enum for key gen protocol
@app.command()
def ssh_key(
    ctx: typer.Context,
    name: Annotated[
        str,
        typer.Argument(
            help=(
                "a suitable name for the ssh-key (e.g. hereToThere) so you "
                "will be able to identify it later."
            )
        ),
    ],
    protocol: Annotated[str, typer.Option(
        help="key generation method")] = "ed25519",
    target: Annotated[
        Optional[str],
        typer.Argument(
            help=(
                "path to a remote server. If given, an attempt to send the "
                "public key will be made."
            )
        ),
    ] = None,
    passphrase: Annotated[
        str,
        typer.Option(
            "-p", help="set a passphrase for the key. default: no passphrase."
        ),
    ] = "",
) -> None:
    key = SSHkey(name=name, protocol=protocol,
                 comment=name, passphrase=passphrase)
    key.create()
    if target is not None:
        key.add_to_config(target)
        key.send_to_server(target)


@app.command()
def gln_install(
    ctx: typer.Context,
    username: Annotated[
        Optional[str],
        typer.Option("--username", "-u", help="your username on the hpc."),
    ] = None,
    python: Annotated[
        str, typer.Option("--python", "-p", help="Python version, (e.g. 3.12)")
    ] = "3.12",
) -> None:
    """
    An ssh-key to a github account with access to TheRealGambleLab must be
    present and shared with github before installing
    (Can use ssh-key command). uv must also be installed
    (can use install-deps command).
    """
    cmd = [
        "uv",
        "tool",
        "install",
        "--python",
        python,
    ]

    try:
        run(
            cmd
            + [
                f"git+ssh://{username}@{username}.hpc.einsteinmed.edu/gs/"
                "gsfs0/users/Gamble%20Lab/ria/gamblelab/27b/"
                "f579f-abbb-44c7-9df2-f7af88306267#egg=gln[extensions]"
            ],
            check=True,
        )
    except CalledProcessError:
        try:
            run(
                cmd
                + [
                    "git+file:///gs/gsfs0/users/Gamble%20Lab/ria/gamblelab/"
                    "27b/f579f-abbb-44c7-9df2-f7af88306267"
                    "#egg=gln[on-hpc-extensions]"
                ],
                check=True,
            )
        except CalledProcessError:
            run(
                cmd
                + [
                    "git+ssh://git@github.com/TheRealGambleLab"
                    "/gln#egg=gln[extensions]"
                ],
                check=True,
            )
