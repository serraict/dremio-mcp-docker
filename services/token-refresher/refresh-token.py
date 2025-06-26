#!/usr/bin/env python3
"""
Dremio Token Refresher

Automatically refreshes Dremio authentication tokens.
"""

import os
import sys
import time
import requests
import logging
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TokenRefresher:
    def __init__(self):
        self.dremio_uri = os.environ["DREMIO_URI"]
        self.username = os.environ["DREMIO_USERNAME"]
        self.password = os.environ["DREMIO_PASSWORD"]
        self.token_file = os.environ["TOKEN_FILE"]

    def get_fresh_token(self) -> Optional[str]:
        """Authenticate with Dremio and get a fresh token."""
        try:
            login_url = f"{self.dremio_uri.rstrip('/')}/apiv2/login"
            payload = {"userName": self.username, "password": self.password}

            logger.info(f"Requesting new token from {login_url}")
            response = requests.post(login_url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            token = data["token"]
            expires_ms = data.get("expires")

            if expires_ms:
                expires_time = datetime.fromtimestamp(expires_ms / 1000)
                logger.info(f"New token expires at: {expires_time}")

            return token

        except requests.RequestException as e:
            logger.error(f"Failed to get token from Dremio: {e}")
            return None
        except KeyError as e:
            logger.error(f"Invalid response format: {e}")
            return None

    def write_token(self, token: str) -> bool:
        """Write token to the shared token file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.token_file), exist_ok=True)

            # Write token atomically
            temp_file = f"{self.token_file}.tmp"
            with open(temp_file, "w") as f:
                f.write(token)

            os.rename(temp_file, self.token_file)
            logger.info(f"Token written to {self.token_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to write token: {e}")
            return False

    def refresh_token(self) -> bool:
        """Complete token refresh process."""
        logger.info("Starting token refresh process")

        # Get fresh token
        token = self.get_fresh_token()
        if not token:
            return False

        # Write token to file
        if not self.write_token(token):
            return False

        logger.info("Token refresh completed successfully")
        return True

    def run_once(self) -> bool:
        """Run token refresh once."""
        return self.refresh_token()

    def run_daemon(self, interval_seconds: int = 72000):  # 20 hours default
        """Run token refresh daemon."""
        logger.info(f"Starting token refresh daemon (interval: {interval_seconds}s)")

        # Initial token refresh
        if not self.refresh_token():
            logger.error("Initial token refresh failed")
            sys.exit(1)

        # Schedule periodic refreshes
        while True:
            try:
                logger.info(
                    f"Sleeping for {interval_seconds} seconds until next refresh"
                )
                time.sleep(interval_seconds)

                if not self.refresh_token():
                    logger.error("Token refresh failed, will retry on next cycle")

            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down")
                break
            except Exception as e:
                logger.error(f"Unexpected error in daemon loop: {e}")
                time.sleep(60)  # Wait a minute before retrying


def main():
    """Main entry point."""
    try:
        refresher = TokenRefresher()

        # Check if running in one-shot mode
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            success = refresher.run_once()
            sys.exit(0 if success else 1)

        # Run as daemon
        interval = int(os.environ.get("REFRESH_INTERVAL", 72000))
        refresher.run_daemon(interval)

    except KeyError as e:
        logger.error(f"Missing required environment variable: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
