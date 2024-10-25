from pathlib import Path
from typing import Annotated, Optional
from types import SimpleNamespace
from warnings import warn
import tomllib

import typer

from .setupUtil import GitInfo

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
    if not hasattr(ctx, "obj") or ctx.obj is None or not hasattr(ctx.obj, "config"):
        with configPath.open("rb") as file:
            ctx.obj = SimpleNamespace(config=tomllib.load(file))

@app.command()
def git(
    ctx: typer.Context,
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
        
