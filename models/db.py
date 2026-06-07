import sqlite3
import os
import threading
from contextlib import contextmanager
from typing import Generator
import config
from models.schema import SchemaMixin, _migrate_db_to_subdir
from models.mixins import (
    EvaluationMixin,
    TestingMixin,
    ToolsMixin,
    AgentMixin,
    ChannelMixin,
    ChatDelegationMixin,
    SettingsMixin,
    ScheduleMixin,
    DashboardMixin,
    ModelsMixin,
    WorkplaceMixin,
    PortalMixin,
    SafetyRuleMixin,
    AttachmentsMixin,
    UserMixin,
    TransferJobMixin,
)


class Database(
    UserMixin,
    SchemaMixin,
    EvaluationMixin,
    TestingMixin,
    ToolsMixin,
    AgentMixin,
    ChannelMixin,
    ChatDelegationMixin,
    SettingsMixin,
    ScheduleMixin,
    DashboardMixin,
    ModelsMixin,
    WorkplaceMixin,
    PortalMixin,
    SafetyRuleMixin,
    AttachmentsMixin,
    TransferJobMixin,
):
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        _migrate_db_to_subdir(db_path)
        self._conn = None
        self._lock = threading.Lock()
        self._init_tables()

    def _get_conn(self) -> sqlite3.Connection:
        """Return the single persistent connection, creating it if needed."""
        if self._conn is not None:
            try:
                self._conn.execute("SELECT 1")
                return self._conn
            except Exception:
                self._conn = None
        conn = sqlite3.connect(f"file:{self.db_path}?mode=rwc&busy_timeout=10000", uri=True)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA wal_autocheckpoint=1000")
        conn.execute("PRAGMA cache_size=-8000")
        conn.execute("PRAGMA mmap_size=268435456")
        self._conn = conn
        return conn

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager returning a shared persistent connection.

        One connection total (not per-thread) prevents file descriptor
        exhaustion from SSE threads that pile up during rapid page navigation.
        """
        with self._lock:
            conn = self._get_conn()
            with conn:
                yield conn

    def close(self):
        """Explicitly close the persistent connection."""
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None


# Re-export chat classes for backward compatibility
from models.chat import AgentChatDB, AgentChatManager, agent_chat_manager  # noqa: F401

# Global singleton
db = Database()
