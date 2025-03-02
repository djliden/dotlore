import click
import yaml
import json
import os
from pathlib import Path
from dotlore.core import config as config_module
from dotlore.core.db import DotLoreDB

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli():
    """DotLore: Context management for code and research projects."""
    pass

@cli.command()
@click.option('--force', is_flag=True, help='Force reinitialization')
def init(force):
    """Initialize DotLore in the current directory."""
    click.echo("Initializing DotLore...")
    
    # Create .lore directory
    lore_dir = Path('.lore')
    if lore_dir.exists() and not force:
        click.echo(".lore directory already exists. Use --force to reinitialize.")
        return
    
    lore_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (lore_dir / 'db').mkdir(exist_ok=True)
    (lore_dir / 'sources').mkdir(exist_ok=True)
    (lore_dir / 'sources' / 'web').mkdir(exist_ok=True)
    (lore_dir / 'sources' / 'files').mkdir(exist_ok=True)
    (lore_dir / 'sources' / 'text').mkdir(exist_ok=True)
    
    # Create default config file
    config_path = config_module.create_default_config()
    click.echo(f"Created default configuration at {config_path}")
    
    # Initialize database
    db = DotLoreDB()
    click.echo(f"Initialized LanceDB database at {db.db_path}")
    
    # Add .lore to .gitignore if it exists
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        if '.lore/' not in content:
            with open(gitignore_path, 'a') as f:
                f.write('\n# DotLore context directory\n.lore/\n')
            click.echo("Added .lore/ to .gitignore")
    
    click.echo("DotLore initialization complete!")

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
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table',
              help='Output format')
def list(format):
    """List all indexed sources."""
    try:
        db = DotLoreDB()
        sources = db.list_sources()
        
        if not sources:
            click.echo("No sources indexed yet.")
            return
        
        if format == 'json':
            click.echo(json.dumps(sources, indent=2))
        else:
            # Table format
            click.echo("\nIndexed Sources:")
            click.echo("-" * 80)
            click.echo(f"{'SOURCE ID':<20} {'TYPE':<10} {'PATH':<40} {'UPDATED':<20}")
            click.echo("-" * 80)
            
            for source in sources:
                click.echo(f"{source['source_id']:<20} {source['source_type']:<10} "
                           f"{source['source_path'][:40]:<40} {source['last_updated']:<20}")
    
    except Exception as e:
        click.echo(f"Error listing sources: {str(e)}")

@cli.command()
def status():
    """Show context statistics."""
    try:
        db = DotLoreDB()
        stats = db.get_db_stats()
        
        click.echo("\nDotLore Context Statistics:")
        click.echo("-" * 50)
        click.echo(f"Total sources: {stats['sources_count']}")
        click.echo(f"Total chunks: {stats['chunks_count']}")
        click.echo(f"Source types: {', '.join(stats['source_types']) if stats['source_types'] else 'None'}")
        
        # Get configuration info
        config = config_module.get_config_value()
        if config:
            click.echo("\nConfiguration:")
            click.echo(f"Embedding model: {config.get('embedding', {}).get('model', 'Not set')}")
            click.echo(f"Chunk size: {config.get('retrieval', {}).get('chunk_size', 'Not set')}")
            click.echo(f"Max context length: {config.get('retrieval', {}).get('max_context_length', 'Not set')}")
    
    except Exception as e:
        click.echo(f"Error getting status: {str(e)}")

@cli.command()
@click.argument('source_id')
@click.option('--force', is_flag=True, help='Force removal without confirmation')
def remove(source_id, force):
    """Remove a source from the context."""
    try:
        db = DotLoreDB()
        source = db.get_source(source_id)
        
        if not source:
            click.echo(f"Source '{source_id}' not found.")
            return
        
        if not force:
            if not click.confirm(f"Are you sure you want to remove '{source_id}' ({source['source_type']}: {source['source_path']})?"):
                click.echo("Removal cancelled.")
                return
        
        db.remove_source(source_id)
        click.echo(f"Removed source: {source_id}")
    
    except Exception as e:
        click.echo(f"Error removing source: {str(e)}")

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
