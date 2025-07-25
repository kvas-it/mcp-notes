import argparse
from pathlib import Path

from .storage import Storage
from .mcp_server import app


def main():
    parser = argparse.ArgumentParser(description='MCP Notes Server')
    parser.add_argument(
        '--dir', type=Path, required=True, help='Directory to store notes'
    )
    args = parser.parse_args()

    app.storage = Storage(args.dir)
    app.run()


if __name__ == '__main__':
    main()
