# wikitree-mcp

MCP server exposing [WikiTree's](https://www.wikitree.com/) genealogy API as tools for Claude Desktop and Claude Code. Public profiles only — no authentication required.

## Available Tools

| Tool | Description |
|---|---|
| `get_profile` | Retrieve a person or free-space profile |
| `get_person` | Retrieve a person profile (person profiles only) |
| `get_people` | Fetch multiple profiles by keys or relationships |
| `search_person` | Search profiles by name, dates, location, gender |
| `get_ancestors` | Get ancestor tree (parents, grandparents, etc.) |
| `get_descendants` | Get descendant tree (children, grandchildren, etc.) |
| `get_relatives` | Get parents, children, siblings, spouses |
| `get_bio` | Retrieve biography text |
| `get_photos` | Get photos linked to a profile |
| `get_categories` | Retrieve associated categories |

## Configuration

| Environment Variable | Required | Default | Description |
|---|---|---|---|
| `WIKITREE_APP_ID` | No | `Genealogy-MCP_wikitree-mcp` | Your application identifier for the WikiTree API |
| `WIKITREE_API_BASE_URL` | No | `https://api.wikitree.com/api.php` | WikiTree API endpoint |
| `WIKITREE_HTTP_TIMEOUT` | No | `10.0` | HTTP request timeout in seconds |
| `WIKITREE_MAX_RETRIES` | No | `3` | Max retry attempts for transient failures |

## Setup: Claude Desktop

Add to your `claude_desktop_config.json`:

### Using uv (local)

```json
{
  "mcpServers": {
    "wikitree": {
      "command": "uv",
      "args": ["--directory", "/path/to/wikitree-mcp", "run", "wikitree-mcp"],
      "env": {
        "WIKITREE_APP_ID": "your-app-id"
      }
    }
  }
}
```

### Using Docker

```json
{
  "mcpServers": {
    "wikitree": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "WIKITREE_APP_ID=your-app-id", "wikitree-mcp"]
    }
  }
}
```

## Setup: Claude Code

### Using uv (local)

```bash
claude mcp add wikitree -- uv --directory /path/to/wikitree-mcp run wikitree-mcp
```

Set the environment variable:

```bash
export WIKITREE_APP_ID=your-app-id
```

### Using Docker

```bash
claude mcp add wikitree -- docker run -i --rm -e WIKITREE_APP_ID=your-app-id wikitree-mcp
```

## Development

```bash
# Install dependencies
make install

# Run tests with coverage (mocked, no network)
make test

# Run live tests against the real WikiTree API
make test-live

# Run all checks (lint + type-check + test)
make check

# Format code
make format

# Build wheel
make build
```

## License

MIT
