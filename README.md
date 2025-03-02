# DotLore

Local context ingestion, storage, and retrieval for AI-assisted writing, research, and development.

## Installation

```bash
# Install using uv tool
uv tool install dotlore

# Or with pip
pip install dotlore
```

## Usage

```bash
# Initialize DotLore in your project
dotlore init

# Add content to your context
dotlore add file.py
dotlore add https://example.com/page
dotlore add --docs https://docs.example.com

# Query your context
dotlore query "How does the authentication system work?"

# Manage your context
dotlore list
dotlore status
dotlore remove source
dotlore update

# Configure DotLore
dotlore config
dotlore config set embedding.model text-embedding-3-small

# Export/Import context
dotlore export context.json
dotlore import context.json
```

See the [design document](designdoc.md) for more details.
