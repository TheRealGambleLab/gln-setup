from pathlib import Path
from typing import Annotated, Optional
from warnings import warn
import tomllib

import typer

from .gitSetup import GitInfo
from .dependencySetup import install_dependencies
from .sshSetup import SSHkey

app = typer.Typer()

@app.callback()
def main(
    ctx: typer.Context,
    configPath: Annotated[
        Path,
        typer.Option("-C", help="Path to a non-default config.toml file for the gln."),
    ] = Path(typer.get_app_dir("gln"), "config.toml"),
) -> None:
    """
    Plugin for the gln to automte system setup.
    """
    pass

@app.command()
def git(
    ctx: typer.Context, #is this needed?
    name: Annotated[
        Optional[str],
        typer.Option(help="enter your first and last name (e.g. 'John Doe')")
    ] = None,
    email: Annotated[
        Optional[str],
        typer.Option(help="enter your email address.")
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force/", "-f/",)
    ] = False,
    file: Annotated[
        Optional[Path],
        typer.Option(hidden=True),
    ] = None,
) -> None:
    gi = GitInfo(file)
    if not gi.installed:
        raise CalledProcessError("git was not found on system.")
    gi.set_name(name, force)
    gi.set_email(email, force)
        
@app.command()
def install_deps(
    ctx: typer.Context, #is this needed?
) -> None:
    install_dependencies()

#TODO: Need enum for key gen protocol
@app.command()
def ssh_key(
    ctx: typer.Context,
    comment: Annotated[str, typer.Argument(help="short comment to include in public key file. If targeting git@github.com, the comment, must be an email associated with your github account.")],
    name: Annotated[str, typer.Argument(help="a suitable name for the ssh-key")],
    protocol: Annotated[str, typer.Option(help="key generation method")] = "ed25519",
    target: Annotated[Optional[str], typer.Argument(help="path to a remote server. If given, an attempt to send the public key will be made.")] = None,
) -> None:
    key = SSHkey(name=name, protocol=protocol, comment=comment,)
    key.create()
    if target is not None:
        key.add_to_config(target)
        key.send_to_server(target)

@app.command()
def gln_config(
    ctx: typer.Context,
) -> None:
    #TODO: What do I really need to add. RIA should control [[ria]], index should control [[query]] and index and template should control templates. The question is, do those each have a setup command in their groups, or do I collect them here and write the appropriate section??
    pass


