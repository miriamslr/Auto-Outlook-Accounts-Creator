#!/usr/bin/env python3
"""
Proxy Manager
Manages proxy rotation for requests
"""

import logging
import random
import threading
from typing import List, Optional


class ProxyManager:
    """Manages proxy rotation"""

    def __init__(self, proxy_file: str):
        self.proxies = self._load_proxies(proxy_file)
        self.current_index = 0
        self.lock = threading.Lock()
        logging.info(f"Loaded {len(self.proxies)} proxies")

    def _load_proxies(self, proxy_file: str) -> List[str]:
        """Load proxies from file"""
        try:
            with open(proxy_file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
            return proxies
        except FileNotFoundError:
            logging.error(f"Proxy file not found: {proxy_file}")
            return []

    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None

        with self.lock:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy

    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
