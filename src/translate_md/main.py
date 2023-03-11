"""Command Line Application for translate-md. """

from pathlib import Path
from typing import Optional

import typer
from rich.progress import Progress

from .client import SpanglishClient

app = typer.Typer()


@app.command()
def main(
    filename: Path = typer.Argument(..., help="Path to markdown file to be translated"),
    new_filename: Optional[Path] = typer.Option(
        None,
        help="Filename for the new markdown file to be generated. If not given, "
        "it is generated internally.",
    ),
):  # pragma: no cover
    """CLI for SpanglishClient, translate markdown files
    from the console.
    """
    with Progress(transient=True) as progress:
        progress.add_task("Running...", total=None)
        client = SpanglishClient()
        client.translate_file(filename, new_filename=new_filename)


if __name__ == "__main__":
    app()
