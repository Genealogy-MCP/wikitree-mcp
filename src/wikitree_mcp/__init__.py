from wikitree_mcp.server import create_server


def main() -> None:
    mcp = create_server()
    mcp.run()


__all__ = ["main", "create_server"]
