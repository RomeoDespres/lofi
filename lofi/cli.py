import click

import lofi


@click.group
def main() -> None:
    """Main CLI entry point."""
    pass


@main.command
def etl() -> None:
    """Run main ETL."""
    lofi.etl.run()
