import logging
import sqlite3

logger = logging.getLogger("discord")

class DatabaseManager:
    def __init__(self):
        self.db_path = "data/db.sqlite"
        self._create_db()

    def _execute(self, query: str, params: tuple = (), fetch: str = None, size: int = None):
        """
        A centralised wrapper that handles connections safely.
        Automatically commits and closes to prevent database locking.
        """
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)

                if fetch == "one":
                    return cursor.fetchone()
                elif fetch == "many":
                    return cursor.fetchmany(size)
                elif fetch == "all":
                    return cursor.fetchall()

                return 1
            except Exception as e:
                logger.error(f"Database error on query '{query}': {e}")
                return -1

    def _create_db(self):
        channels_table = """
        CREATE TABLE IF NOT EXISTS hp_channels (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            punishment TEXT NOT NULL,
            duration INTEGER NOT NULL
        )
        """

        perms_table = """
        CREATE TABLE IF NOT EXISTS perms (
            guild_id INTEGER NOT NULL PRIMARY KEY,
            role_id INTEGER NOT NULL
        )
        """

        logs_table = """
        CREATE TABLE IF NOT EXISTS logs (
            guild_id INTEGER NOT NULL PRIMARY KEY,
            channel_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL
        )
        """

        self._execute(channels_table)
        self._execute(perms_table)
        self._execute(logs_table)

    def get_channels(self, guild_id: int):
        query = "SELECT * FROM hp_channels WHERE guild_id = ?"
        return self._execute(query, (guild_id,), fetch="all")

    def get_channel(self, guild_id: int, channel_id: int):
        query = "SELECT * FROM hp_channels WHERE guild_id = ? and channel_id = ?"
        return self._execute(query, (guild_id, channel_id), fetch="one")

    def get_perms(self, guild_id: int):
        query = "SELECT * FROM perms WHERE guild_id = ?"
        return self._execute(query, (guild_id,), fetch="one")

    def get_logs(self, guild_id: int):
        query = "SELECT * FROM logs WHERE guild_id = ?"
        return self._execute(query, (guild_id,), fetch="one")

    def add_channel(self, guild_id: int, channel_id: int, punishment: str, duration: int):
        query = "INSERT INTO hp_channels(guild_id, channel_id, punishment, duration) VALUES (?, ?, ?, ?)"
        self._execute(query, (guild_id, channel_id, punishment, duration))

    def edit_channel(self, guild_id: int, channel_id: int, punishment: str, duration: int):
        query = "UPDATE hp_channels SET punishment = ?, duration = ? WHERE guild_id = ? and channel_id = ?"
        self._execute(query, (punishment, duration, guild_id, channel_id))

    def remove_channel(self, guild_id: int, channel_id: int):
        query = "DELETE FROM hp_channels WHERE guild_id = ? and channel_id = ?"
        self._execute(query, (guild_id, channel_id))

    def configure_perms(self, guild_id: int, role_id: int):
        select_query = "SELECT * FROM perms WHERE guild_id = ?"

        if self._execute(select_query, (guild_id, ), fetch="all") == []:
            query = "INSERT INTO perms(guild_id, role_id) VALUES (?, ?)"
            self._execute(query, (guild_id, role_id))
        else:
            query = "UPDATE perms SET role_id = ? WHERE guild_id = ?"
            self._execute(query, (role_id, guild_id))

    def configure_logs(self, guild_id: int, channel_id: int, role_id: int):
        select_query = "SELECT * FROM logs WHERE guild_id = ?"

        if self._execute(select_query, (guild_id, ), fetch="all") == []:
            query = "INSERT INTO logs VALUES (?, ?, ?)"
            self._execute(query, (guild_id, channel_id, role_id))
        else:
            query = "UPDATE logs SET channel_id = ?, role_id = ? WHERE guild_id = ?"
            self._execute(query, (channel_id, role_id, guild_id))
