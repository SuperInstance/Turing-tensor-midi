"""Entry point for ``python -m turing``."""

from __future__ import annotations

import signal
import sys

from .listener import TuringListener


def main() -> None:
    listener = TuringListener()

    def _shutdown(sig: int, _frame: object) -> None:
        listener.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)
    listener.run()


if __name__ == "__main__":
    main()
