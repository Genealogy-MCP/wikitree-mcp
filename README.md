# wikitree-mcp

MCP server exposing [WikiTree's](https://www.wikitree.com/) genealogy API via the Code Mode architecture. Public profiles only — no authentication required.

**Note:** GitHub is a read-only mirror. Development happens on [GitLab](https://gitlab.com/genealogy-mcp/wikitree-mcp).

## Architecture

This server uses 2 meta-tools (`search` + `execute`) with 10 operations in a server-side registry. The LLM discovers operations via `search` and runs them via `execute`.

| Tool | Description |
|---|---|
| `search` | Discover available operations and their parameters |
| `execute` | Run a named operation against the WikiTree API |

### Operations

| Operation | Category | Description |
|---|---|---|
| `get_profile` | read | Retrieve a person or free-space profile |
| `get_person` | read | Retrieve a person profile (person profiles only) |
| `get_people` | read | Fetch multiple profiles by keys or relationships |
| `search_person` | search | Search profiles by name, dates, location, gender |
| `get_ancestors` | analysis | Get ancestor tree (parents, grandparents, etc.) |
| `get_descendants` | analysis | Get descendant tree (children, grandchildren, etc.) |
| `get_relatives` | read | Get parents, children, siblings, spouses |
| `get_bio` | content | Retrieve biography text |
| `get_photos` | content | Get photos linked to a profile |
| `get_categories` | content | Retrieve associated categories |

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
make install       # Install dependencies
make test          # Run tests with coverage (mocked, no network)
make test-live     # Run live tests against real WikiTree API
make ci            # Full CI pipeline (lint + typecheck + test + audit)
make format        # Auto-format code
make build         # Build wheel
make run           # Run with streamable-http on port 8000
make run-stdio     # Run with stdio transport
```

## License

AGPL-3.0-only
