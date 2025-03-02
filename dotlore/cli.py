import click
import yaml
from dotlore.core import config as config_module

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli():
    """DotLore: Context management for code and research projects."""
    pass

@cli.command()
def init():
    """Initialize DotLore in the current directory."""
    click.echo("Initializing DotLore...")
    
    # Create default config file
    config_path = config_module.create_default_config()
    click.echo(f"Created default configuration at {config_path}")

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
@click.option('--set', is_flag=True, help='Set a configuration value')
def config(key, value, set):
    """View or set configuration."""
    config_path = config_module.get_config_path()
    
    if not config_path.exists():
        click.echo("No configuration found. Run 'dotlore init' first.")
        return
    
    if set and key and value:
        config_module.set_config_value(key, value)
        click.echo(f"Set config {key} to {value}")
    elif key:
        config_value = config_module.get_config_value(key)
        if config_value is not None:
            if isinstance(config_value, (dict, list)):
                click.echo(yaml.dump({key: config_value}, default_flow_style=False))
            else:
                click.echo(f"{key}: {config_value}")
        else:
            click.echo(f"No configuration found for {key}")
    else:
        # Show all configuration
        cfg = config_module.get_config_value()
        if cfg:
            click.echo(yaml.dump(cfg, default_flow_style=False))
        else:
            click.echo("No configuration found")

@cli.command()
@click.argument('filename')
def export(filename):
    """Export context to file."""
    click.echo(f"Exporting context to {filename}")

@cli.command(name='import')
@click.argument('filename')
def import_(filename):
    """Import context from file."""
    click.echo(f"Importing context from {filename}")

if __name__ == '__main__':
    cli()
