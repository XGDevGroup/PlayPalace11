"""Entry point for running the PlayPalace v11 server with uv run main.py."""

import argparse
import asyncio
import sys
import os

# Ensure we can import from the package correctly
_script_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_script_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Change to script directory so relative paths work
os.chdir(_script_dir)

from server.core.server import run_server  # noqa: E402


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PlayPalace v11 Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on default port (8000) without SSL
  uv run python main.py

  # Run on custom port
  uv run python main.py --port 9000

  # Run with SSL (WSS) using Let's Encrypt certificates
  uv run python main.py --ssl-cert /etc/letsencrypt/live/example.com/fullchain.pem \\
                        --ssl-key /etc/letsencrypt/live/example.com/privkey.pem

  # Run with SSL on custom port
  uv run python main.py --port 8443 --ssl-cert cert.pem --ssl-key key.pem
""",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host address to bind to (default: 127.0.0.1 or [server].bind_ip)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port number to listen on (overrides config; default: 8000)",
    )
    parser.add_argument(
        "--ssl-cert",
        dest="ssl_cert",
        help="Path to SSL certificate file (enables WSS). For Let's Encrypt, use fullchain.pem",
    )
    parser.add_argument(
        "--ssl-key",
        dest="ssl_key",
        help="Path to SSL private key file. For Let's Encrypt, use privkey.pem",
    )
    parser.add_argument(
        "--preload-locales",
        action="store_true",
        help="Block startup until all localization bundles compile (default: warm in background).",
    )

    args = parser.parse_args()

    # Validate SSL arguments (CLI-supplied; config-supplied is validated inside run_server)
    if (args.ssl_cert and not args.ssl_key) or (args.ssl_key and not args.ssl_cert):
        parser.error("Both --ssl-cert and --ssl-key must be provided together")

    asyncio.run(
        run_server(
            host=args.host,
            port=args.port,
            ssl_cert=args.ssl_cert,
            ssl_key=args.ssl_key,
            preload_locales=args.preload_locales,
        )
    )


if __name__ == "__main__":
    main()
