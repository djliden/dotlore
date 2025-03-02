import click

@click.group()
def cli():
    """DotLore: Context management for code and research projects."""
    pass

@cli.command()
def init():
    """Initialize DotLore in the current directory."""
    click.echo("Initializing DotLore...")

@cli.command()
@click.argument('sources', nargs=-1)
@click.option('--docs', is_flag=True, help='Crawl documentation site')
def add(sources, docs):
    """Add source(s) to the context."""
    if docs:
        click.echo(f"Adding documentation site: {sources}")
    else:
        click.echo(f"Adding sources: {sources}")

@cli.command()
def list():
    """List all indexed sources."""
    click.echo("Listing all indexed sources...")

@cli.command()
def status():
    """Show context statistics."""
    click.echo("Showing context statistics...")

@cli.command()
@click.argument('source')
def remove(source):
    """Remove a source from the context."""
    click.echo(f"Removing source: {source}")

@cli.command()
@click.argument('source', required=False)
def update(source):
    """Update all or specific sources."""
    if source:
        click.echo(f"Updating source: {source}")
    else:
        click.echo("Updating all sources...")

@cli.command()
@click.argument('query')
def query(query):
    """Retrieve context for a query."""
    click.echo(f"Querying: {query}")

@cli.command()
@click.argument('key', required=False)
@click.argument('value', required=False)
def config(key, value):
    """View or set configuration."""
    if key and value:
        click.echo(f"Setting config {key} to {value}")
    elif key:
        click.echo(f"Getting config value for {key}")
    else:
        click.echo("Showing all configuration")

@cli.command()
@click.argument('filename')
def export(filename):
    """Export context to file."""
    click.echo(f"Exporting context to {filename}")

@cli.command()
@click.argument('filename')
def import_(filename):
    """Import context from file."""
    click.echo(f"Importing context from {filename}")

if __name__ == '__main__':
    cli()
