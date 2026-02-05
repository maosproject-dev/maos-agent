import signal
import sys
import logging

class SpotInterruptionError(Exception):
    """Raised when the environment signals a shutdown."""
    pass

class LifecycleManager:
    def __init__(self):
        self.should_exit = False
        self.logger = logging.getLogger("maos.lifecycle")
        
        # Register the signal handlers
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        signal.signal(signal.SIGINT, self._handle_sigterm) # Handle Ctrl+C locally too

    def _handle_sigterm(self, signum, frame):
        self.logger.warning("⚠️ SIGTERM received from Kubernetes! Node is draining.")
        self.should_exit = True

    def check_health(self):
        """
        Call this inside your agent loop.
        If a kill signal was received, it raises an exception to break the loop safely.
        """
        if self.should_exit:
            raise SpotInterruptionError("Spot Instance Reclaim Imminent")