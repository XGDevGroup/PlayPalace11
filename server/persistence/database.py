"""SQLite database for persistence."""

import sqlite3
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field

from server.core.tables.table import Table
from server.core.users.base import TrustLevel


@dataclass
class UserRecord:
    """User record loaded from the database.

    Attributes:
        id: Internal numeric id.
        username: Username (display name).
        password_hash: Stored password hash.
        uuid: Persistent UUID for stats tracking.
        locale: Preferred locale.
        preferences_json: JSON preferences blob.
        trust_level: Trust level for permissions.
        approved: Whether the account is approved.
        fluent_languages: Languages the user knows.
    """

    id: int
    username: str
    password_hash: str
    uuid: str  # Persistent unique identifier for stats tracking
    locale: str = "en"
    preferences_json: str = "{}"
    trust_level: TrustLevel = TrustLevel.USER
    approved: bool = False  # Whether the account has been approved by an admin
    fluent_languages: list[str] = field(default_factory=list)


@dataclass
class SavedTableRecord:
    """Saved table record from the database.

    Attributes:
        id: Internal numeric id.
        username: Owner username.
        save_name: User-visible save name.
        game_type: Game type identifier.
        game_json: Serialized game state.
        members_json: Serialized member list.
        saved_at: Timestamp string.
    """

    id: int
    username: str
    save_name: str
    game_type: str
    game_json: str
    members_json: str
    saved_at: str


@dataclass
class RefreshTokenRecord:
    """Refresh token record loaded from the database.

    Attributes:
        username: Owner username.
        token: The token string.
        expires_at: Expiration epoch timestamp.
        created_at: Creation epoch timestamp.
        revoked_at: Revocation epoch timestamp, or None if active.
        replaced_by: Replacement token string, or None.
    """

    username: str
    token: str
    expires_at: int
    created_at: int
    revoked_at: int | None = None
    replaced_by: str | None = None


def _token_from_row(row: sqlite3.Row) -> RefreshTokenRecord:
    """Build a RefreshTokenRecord from a database row."""
    return RefreshTokenRecord(
        username=row["username"],
        token=row["token"],
        expires_at=row["expires_at"],
        created_at=row["created_at"],
        revoked_at=row["revoked_at"],
        replaced_by=row["replaced_by"],
    )


class Database:
    """SQLite database for PlayPalace persistence.

    Stores users, tables, saved tables, and game results.
    """

    def __init__(self, db_path: str | Path = "playpalace.db"):
        """Initialize the database wrapper with a path."""
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    def _get_conn(self) -> sqlite3.Connection:
        """Return the active connection or raise if not connected."""
        if self._conn is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    def connect(self) -> None:
        """Connect to the database and create tables if needed."""
        try:
            self._conn = sqlite3.connect(str(self.db_path))
        except sqlite3.Error as exc:
            print(
                f"ERROR: Failed to open database at '{self.db_path}': {exc}",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self._get_conn().cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                uuid TEXT NOT NULL,
                locale TEXT DEFAULT 'en',
                preferences_json TEXT DEFAULT '{}',
                trust_level INTEGER DEFAULT 1,
                approved INTEGER DEFAULT 0,
                fluent_languages TEXT DEFAULT '[]'
            )
        """)

        # Transcriber assignments (languages a user is approved to transcribe)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcriber_assignments (
                user_id INTEGER NOT NULL,
                lang_code TEXT NOT NULL,
                PRIMARY KEY (user_id, lang_code),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Tables table (game tables)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tables (
                table_id TEXT PRIMARY KEY,
                game_type TEXT NOT NULL,
                host TEXT NOT NULL,
                members_json TEXT NOT NULL,
                game_json TEXT,
                status TEXT DEFAULT 'waiting'
            )
        """)

        # Saved tables (user-saved game states)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                save_name TEXT NOT NULL,
                game_type TEXT NOT NULL,
                game_json TEXT NOT NULL,
                members_json TEXT NOT NULL,
                saved_at TEXT NOT NULL
            )
        """)

        # Game results (for statistics)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration_ticks INTEGER,
                custom_data TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_result_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER REFERENCES game_results(id) ON DELETE CASCADE,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                is_bot INTEGER NOT NULL,
                is_virtual_bot INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Indexes for game results
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_results_type
            ON game_results(game_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_results_timestamp
            ON game_results(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_result_players_player
            ON game_result_players(player_id)
        """)

        # Player ratings (for skill-based matchmaking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_ratings (
                player_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                mu REAL NOT NULL,
                sigma REAL NOT NULL,
                PRIMARY KEY (player_id, game_type)
            )
        """)

        # Refresh tokens for session renewal
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at INTEGER NOT NULL,
                revoked_at INTEGER,
                replaced_by TEXT
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_username
            ON refresh_tokens(username)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires
            ON refresh_tokens(expires_at)
        """)

        self._get_conn().commit()

        # Run migrations for existing databases
        self._run_migrations()

    def _run_migrations(self) -> None:
        """Run database migrations for existing databases."""
        cursor = self._get_conn().cursor()

        # Check which columns exist in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]

        if "trust_level" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN trust_level INTEGER DEFAULT 1")
            self._get_conn().commit()

        if "approved" not in columns:
            # Add approved column - existing users are auto-approved
            cursor.execute("ALTER TABLE users ADD COLUMN approved INTEGER DEFAULT 0")
            cursor.execute("UPDATE users SET approved = 1")  # Approve all existing users
            self._get_conn().commit()

        # Check game_result_players for is_virtual_bot column
        cursor.execute("PRAGMA table_info(game_result_players)")
        grp_columns = [row[1] for row in cursor.fetchall()]

        if "is_virtual_bot" not in grp_columns:
            cursor.execute(
                "ALTER TABLE game_result_players ADD COLUMN is_virtual_bot INTEGER DEFAULT 0"
            )
            self._get_conn().commit()

        try:
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_lower ON users(lower(username))"
            )
            self._get_conn().commit()
        except sqlite3.IntegrityError as exc:
            print(
                "ERROR: Duplicate usernames exist when compared case-insensitively. "
                "Please resolve duplicates before restarting the server.",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc

        if "fluent_languages" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN fluent_languages TEXT DEFAULT '[]'")
            self._get_conn().commit()

        # Ensure transcriber_assignments table exists for older databases
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transcriber_assignments'"
        )
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transcriber_assignments (
                    user_id INTEGER NOT NULL,
                    lang_code TEXT NOT NULL,
                    PRIMARY KEY (user_id, lang_code),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            self._get_conn().commit()

        # Ensure refresh_tokens table exists for older databases
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='refresh_tokens'"
        )
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at INTEGER NOT NULL,
                    created_at INTEGER NOT NULL,
                    revoked_at INTEGER,
                    replaced_by TEXT
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_refresh_tokens_username
                ON refresh_tokens(username)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires
                ON refresh_tokens(expires_at)
            """)
            self._get_conn().commit()

    # User operations

    @staticmethod
    def _user_from_row(row: sqlite3.Row) -> UserRecord:
        """Build a UserRecord from a database row."""
        trust_level_int = row["trust_level"] if row["trust_level"] is not None else 1
        return UserRecord(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            uuid=row["uuid"],
            locale=row["locale"] or "en",
            preferences_json=row["preferences_json"] or "{}",
            trust_level=TrustLevel(trust_level_int),
            approved=bool(row["approved"]) if row["approved"] is not None else False,
            fluent_languages=json.loads(row["fluent_languages"] or "[]"),
        )

    _USER_COLUMNS = "id, username, password_hash, uuid, locale, preferences_json, trust_level, approved, fluent_languages"

    def get_user(self, username: str) -> UserRecord | None:
        """Get a user by username."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            f"SELECT {self._USER_COLUMNS} FROM users WHERE lower(username) = lower(?)",
            (username,),
        )
        row = cursor.fetchone()
        if row:
            return self._user_from_row(row)
        return None

    def create_user(
        self,
        username: str,
        password_hash: str,
        locale: str = "en",
        trust_level: TrustLevel = TrustLevel.USER,
        approved: bool = False,
    ) -> UserRecord:
        """Create a new user with a generated UUID.

        Args:
            username: Username (display name).
            password_hash: Hashed password.
            locale: Preferred locale.
            trust_level: Initial trust level.
            approved: Whether the account is approved.

        Returns:
            Created UserRecord.
        """
        import uuid as uuid_module

        user_uuid = str(uuid_module.uuid4())
        cursor = self._get_conn().cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, uuid, locale, trust_level, approved) VALUES (?, ?, ?, ?, ?, ?)",
            (username, password_hash, user_uuid, locale, trust_level.value, 1 if approved else 0),
        )
        self._get_conn().commit()
        return UserRecord(
            id=cursor.lastrowid,
            username=username,
            password_hash=password_hash,
            uuid=user_uuid,
            locale=locale,
            trust_level=trust_level,
            approved=approved,
        )

    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT 1 FROM users WHERE lower(username) = lower(?)", (username,))
        return cursor.fetchone() is not None

    def update_user_locale(self, username: str, locale: str) -> None:
        """Update a user's locale."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            "UPDATE users SET locale = ? WHERE lower(username) = lower(?)", (locale, username)
        )
        self._get_conn().commit()

    def update_user_preferences(self, username: str, preferences_json: str) -> None:
        """Update a user's preferences."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            "UPDATE users SET preferences_json = ? WHERE lower(username) = lower(?)",
            (preferences_json, username),
        )
        self._get_conn().commit()

    def update_user_password(self, username: str, password_hash: str) -> None:
        """Update a user's password hash.

        Args:
            username: Username to update.
            password_hash: New password hash.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE lower(username) = lower(?)",
            (password_hash, username),
        )
        self._get_conn().commit()

    # Refresh token operations

    def store_refresh_token(
        self, username: str, token: str, expires_at: int, created_at: int
    ) -> None:
        """Store a new refresh token."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            "INSERT INTO refresh_tokens (username, token, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (username, token, expires_at, created_at),
        )
        self._get_conn().commit()

    def get_refresh_token(self, token: str) -> RefreshTokenRecord | None:
        """Fetch a refresh token record by token."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            "SELECT username, token, expires_at, created_at, revoked_at, replaced_by "
            "FROM refresh_tokens WHERE token = ?",
            (token,),
        )
        row = cursor.fetchone()
        return _token_from_row(row) if row else None

    def revoke_refresh_token(
        self, token: str, revoked_at: int, replaced_by: str | None = None
    ) -> None:
        """Revoke a refresh token and optionally link its replacement."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            "UPDATE refresh_tokens SET revoked_at = ?, replaced_by = ? WHERE token = ?",
            (revoked_at, replaced_by, token),
        )
        self._get_conn().commit()

    def get_user_count(self) -> int:
        """Get the total number of users in the database."""
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

    def initialize_trust_levels(self) -> str | None:
        """
        Initialize trust levels for users who don't have one set.

        Sets all users without a trust level to USER.
        If there's exactly one user and they have no trust level, sets them to SERVER_OWNER.

        Returns:
            The username of the user promoted to server owner, or None if no promotion occurred.
        """
        cursor = self._get_conn().cursor()

        # Check if there's exactly one user with no trust level set
        cursor.execute("SELECT id, username FROM users WHERE trust_level IS NULL")
        users_without_trust = cursor.fetchall()

        promoted_user = None

        if len(users_without_trust) == 1:
            # Check if this is the only user in the database
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            if total_users == 1:
                # First and only user - make them server owner
                username = users_without_trust[0]["username"]
                cursor.execute(
                    "UPDATE users SET trust_level = ? WHERE id = ?",
                    (TrustLevel.SERVER_OWNER.value, users_without_trust[0]["id"]),
                )
                promoted_user = username

        # Set all remaining users without trust level to USER
        cursor.execute(
            "UPDATE users SET trust_level = ? WHERE trust_level IS NULL", (TrustLevel.USER.value,)
        )
        self._get_conn().commit()

        return promoted_user

    def update_user_trust_level(self, username: str, trust_level: TrustLevel) -> None:
        """Update a user's trust level.

        Args:
            username: Username to update.
            trust_level: New trust level.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            "UPDATE users SET trust_level = ? WHERE lower(username) = lower(?)",
            (trust_level.value, username),
        )
        self._get_conn().commit()

    def get_pending_users(self, exclude_banned: bool = True) -> list[UserRecord]:
        """Get all users who are not yet approved.

        Args:
            exclude_banned: If True (default), excludes banned users from the results.
        """
        cursor = self._get_conn().cursor()
        if exclude_banned:
            cursor.execute(
                f"SELECT {self._USER_COLUMNS} FROM users WHERE approved = 0 AND trust_level > ?",
                (TrustLevel.BANNED.value,),
            )
        else:
            cursor.execute(f"SELECT {self._USER_COLUMNS} FROM users WHERE approved = 0")
        return [self._user_from_row(row) for row in cursor.fetchall()]

    def get_banned_users(self) -> list[UserRecord]:
        """Get all banned users.

        Returns:
            List of banned UserRecords.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            f"SELECT {self._USER_COLUMNS} FROM users WHERE trust_level = ?",
            (TrustLevel.BANNED.value,),
        )
        return [self._user_from_row(row) for row in cursor.fetchall()]

    def approve_user(self, username: str) -> bool:
        """Approve a user account.

        Args:
            username: Username to approve.

        Returns:
            True if user was found and approved.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            "UPDATE users SET approved = 1 WHERE lower(username) = lower(?)",
            (username,),
        )
        self._get_conn().commit()
        return cursor.rowcount > 0

    def delete_user(self, username: str) -> bool:
        """Delete a user account.

        Args:
            username: Username to delete.

        Returns:
            True if user was found and deleted.
        """
        cursor = self._get_conn().cursor()
        cursor.execute("DELETE FROM users WHERE lower(username) = lower(?)", (username,))
        self._get_conn().commit()
        return cursor.rowcount > 0

    def get_non_admin_users(self, exclude_banned: bool = True) -> list[UserRecord]:
        """Get all approved users who are not admins (trust_level < ADMIN).

        Args:
            exclude_banned: If True (default), excludes banned users from the results.
        """
        cursor = self._get_conn().cursor()
        if exclude_banned:
            cursor.execute(
                f"SELECT {self._USER_COLUMNS} FROM users WHERE approved = 1 AND trust_level > ? AND trust_level < ? ORDER BY username",
                (TrustLevel.BANNED.value, TrustLevel.ADMIN.value),
            )
        else:
            cursor.execute(
                f"SELECT {self._USER_COLUMNS} FROM users WHERE approved = 1 AND trust_level < ? ORDER BY username",
                (TrustLevel.ADMIN.value,),
            )
        return [self._user_from_row(row) for row in cursor.fetchall()]

    def get_server_owner(self) -> UserRecord | None:
        """Get the server owner (there should only be one)."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            f"SELECT {self._USER_COLUMNS} FROM users WHERE trust_level = ?",
            (TrustLevel.SERVER_OWNER.value,),
        )
        row = cursor.fetchone()
        if row:
            return self._user_from_row(row)
        return None

    def get_admin_users(self, include_server_owner: bool = True) -> list[UserRecord]:
        """Get all users who are admins (trust_level >= ADMIN).

        Args:
            include_server_owner: If True, includes the server owner in the list.
                                  If False, only returns admins (not server owner).
        """
        cursor = self._get_conn().cursor()
        if include_server_owner:
            cursor.execute(
                f"SELECT {self._USER_COLUMNS} FROM users WHERE trust_level >= ? ORDER BY username",
                (TrustLevel.ADMIN.value,),
            )
        else:
            cursor.execute(
                f"SELECT {self._USER_COLUMNS} FROM users WHERE trust_level = ? ORDER BY username",
                (TrustLevel.ADMIN.value,),
            )
        return [self._user_from_row(row) for row in cursor.fetchall()]

    # Fluent languages operations

    def get_user_fluent_languages(self, username: str) -> list[str]:
        """Get the languages a user knows.

        Args:
            username: Username to look up.

        Returns:
            List of language codes.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            "SELECT fluent_languages FROM users WHERE lower(username) = lower(?)",
            (username,),
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["fluent_languages"] or "[]")
        return []

    def set_user_fluent_languages(self, username: str, languages: list[str]) -> None:
        """Replace a user's fluent languages list.

        Args:
            username: Username to update.
            languages: New list of language codes.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            "UPDATE users SET fluent_languages = ? WHERE lower(username) = lower(?)",
            (json.dumps(languages), username),
        )
        self._get_conn().commit()

    # Transcriber assignment operations

    def get_transcriber_languages(self, username: str) -> list[str]:
        """Get languages a user is approved to transcribe.

        Args:
            username: Username to look up.

        Returns:
            List of assigned language codes.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            "SELECT ta.lang_code FROM transcriber_assignments ta "
            "JOIN users u ON ta.user_id = u.id "
            "WHERE lower(u.username) = lower(?) ORDER BY ta.lang_code",
            (username,),
        )
        return [row["lang_code"] for row in cursor.fetchall()]

    def add_transcriber_assignment(self, username: str, lang_code: str) -> bool:
        """Assign a user as transcriber for a language.

        Args:
            username: Username to assign.
            lang_code: Language code to assign.

        Returns:
            True if added, False if the assignment already exists.
        """
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT id FROM users WHERE lower(username) = lower(?)", (username,))
        row = cursor.fetchone()
        if not row:
            return False
        user_id = row["id"]
        try:
            cursor.execute(
                "INSERT INTO transcriber_assignments (user_id, lang_code) VALUES (?, ?)",
                (user_id, lang_code),
            )
            self._get_conn().commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_transcriber_assignment(self, username: str, lang_code: str) -> bool:
        """Remove a transcriber assignment.

        Args:
            username: Username to remove assignment from.
            lang_code: Language code to remove.

        Returns:
            True if removed, False if the assignment was not found.
        """
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT id FROM users WHERE lower(username) = lower(?)", (username,))
        row = cursor.fetchone()
        if not row:
            return False
        user_id = row["id"]
        cursor.execute(
            "DELETE FROM transcriber_assignments WHERE user_id = ? AND lang_code = ?",
            (user_id, lang_code),
        )
        self._get_conn().commit()
        return cursor.rowcount > 0

    def get_transcribers_for_language(self, lang_code: str) -> list[str]:
        """Get all usernames assigned as transcribers for a language.

        Args:
            lang_code: Language code to look up.

        Returns:
            List of usernames.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            "SELECT u.username FROM transcriber_assignments ta "
            "JOIN users u ON ta.user_id = u.id "
            "WHERE ta.lang_code = ? ORDER BY u.username",
            (lang_code,),
        )
        return [row["username"] for row in cursor.fetchall()]

    def get_all_transcribers(self) -> dict[str, list[str]]:
        """Get all transcriber assignments grouped by username.

        Returns:
            Dict mapping username to list of assigned language codes.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            "SELECT u.username, ta.lang_code FROM transcriber_assignments ta "
            "JOIN users u ON ta.user_id = u.id "
            "ORDER BY u.username, ta.lang_code"
        )
        result: dict[str, list[str]] = {}
        for row in cursor.fetchall():
            result.setdefault(row["username"], []).append(row["lang_code"])
        return result

    # Table operations

    def save_table(self, table: Table) -> None:
        """Save a table to the database."""
        cursor = self._get_conn().cursor()

        # Serialize members
        members_json = json.dumps(
            [{"username": m.username, "is_spectator": m.is_spectator} for m in table.members]
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO tables (table_id, game_type, host, members_json, game_json, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                table.table_id,
                table.game_type,
                table.host,
                members_json,
                table.game_json,
                table.status,
            ),
        )
        self._get_conn().commit()

    def load_table(self, table_id: str) -> Table | None:
        """Load a table from the database."""
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT * FROM tables WHERE table_id = ?", (table_id,))
        row = cursor.fetchone()
        if not row:
            return None

        # Deserialize members
        members_data = json.loads(row["members_json"])
        from server.core.tables.table import TableMember

        members = [
            TableMember(username=m["username"], is_spectator=m["is_spectator"])
            for m in members_data
        ]

        return Table(
            table_id=row["table_id"],
            game_type=row["game_type"],
            host=row["host"],
            members=members,
            game_json=row["game_json"],
            status=row["status"],
        )

    def load_all_tables(self) -> list[Table]:
        """Load all tables from the database."""
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT table_id FROM tables")
        tables = []
        for row in cursor.fetchall():
            table = self.load_table(row["table_id"])
            if table:
                tables.append(table)
        return tables

    def delete_table(self, table_id: str) -> None:
        """Delete a table from the database."""
        cursor = self._get_conn().cursor()
        cursor.execute("DELETE FROM tables WHERE table_id = ?", (table_id,))
        self._get_conn().commit()

    def delete_all_tables(self) -> None:
        """Delete all tables from the database."""
        cursor = self._get_conn().cursor()
        cursor.execute("DELETE FROM tables")
        self._get_conn().commit()

    def save_all_tables(self, tables: list[Table]) -> None:
        """Save multiple tables."""
        for table in tables:
            self.save_table(table)

    # Saved table operations (user-saved game states)

    def save_user_table(
        self,
        username: str,
        save_name: str,
        game_type: str,
        game_json: str,
        members_json: str,
    ) -> SavedTableRecord:
        """Save a table state to a user's saved tables."""
        from datetime import datetime

        saved_at = datetime.now().isoformat()

        cursor = self._get_conn().cursor()
        cursor.execute(
            """
            INSERT INTO saved_tables (username, save_name, game_type, game_json, members_json, saved_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (username, save_name, game_type, game_json, members_json, saved_at),
        )
        self._get_conn().commit()

        return SavedTableRecord(
            id=cursor.lastrowid,
            username=username,
            save_name=save_name,
            game_type=game_type,
            game_json=game_json,
            members_json=members_json,
            saved_at=saved_at,
        )

    def get_user_saved_tables(self, username: str) -> list[SavedTableRecord]:
        """Get all saved tables for a user."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            "SELECT * FROM saved_tables WHERE lower(username) = lower(?) ORDER BY saved_at DESC",
            (username,),
        )
        records = []
        for row in cursor.fetchall():
            records.append(
                SavedTableRecord(
                    id=row["id"],
                    username=row["username"],
                    save_name=row["save_name"],
                    game_type=row["game_type"],
                    game_json=row["game_json"],
                    members_json=row["members_json"],
                    saved_at=row["saved_at"],
                )
            )
        return records

    def get_saved_table(self, save_id: int) -> SavedTableRecord | None:
        """Get a saved table by ID."""
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT * FROM saved_tables WHERE id = ?", (save_id,))
        row = cursor.fetchone()
        if not row:
            return None

        return SavedTableRecord(
            id=row["id"],
            username=row["username"],
            save_name=row["save_name"],
            game_type=row["game_type"],
            game_json=row["game_json"],
            members_json=row["members_json"],
            saved_at=row["saved_at"],
        )

    def delete_saved_table(self, save_id: int) -> None:
        """Delete a saved table."""
        cursor = self._get_conn().cursor()
        cursor.execute("DELETE FROM saved_tables WHERE id = ?", (save_id,))
        self._get_conn().commit()

    # Game result operations (statistics)

    def save_game_result(
        self,
        game_type: str,
        timestamp: str,
        duration_ticks: int,
        players: list[
            tuple[str, str, bool, bool]
        ],  # (player_id, player_name, is_bot, is_virtual_bot)
        custom_data: dict | None = None,
    ) -> int:
        """
        Save a game result to the database.

        Args:
            game_type: The game type identifier
            timestamp: ISO format timestamp
            duration_ticks: Game duration in ticks
            players: List of (player_id, player_name, is_bot, is_virtual_bot) tuples
            custom_data: Game-specific result data

        Returns:
            The result ID
        """
        cursor = self._get_conn().cursor()

        # Insert the main result record
        cursor.execute(
            """
            INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data)
            VALUES (?, ?, ?, ?)
            """,
            (
                game_type,
                timestamp,
                duration_ticks,
                json.dumps(custom_data) if custom_data else None,
            ),
        )
        result_id = cursor.lastrowid

        # Insert player records
        for player_id, player_name, is_bot, is_virtual_bot in players:
            cursor.execute(
                """
                INSERT INTO game_result_players (result_id, player_id, player_name, is_bot, is_virtual_bot)
                VALUES (?, ?, ?, ?, ?)
                """,
                (result_id, player_id, player_name, 1 if is_bot else 0, 1 if is_virtual_bot else 0),
            )

        self._get_conn().commit()
        return result_id

    def get_player_game_history(
        self,
        player_id: str,
        game_type: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        Get a player's game history.

        Args:
            player_id: The player ID to look up
            game_type: Optional filter by game type
            limit: Maximum number of results

        Returns:
            List of game result dictionaries
        """
        cursor = self._get_conn().cursor()

        if game_type:
            cursor.execute(
                """
                SELECT gr.id, gr.game_type, gr.timestamp, gr.duration_ticks, gr.custom_data
                FROM game_results gr
                INNER JOIN game_result_players grp ON gr.id = grp.result_id
                WHERE grp.player_id = ? AND gr.game_type = ?
                ORDER BY gr.timestamp DESC
                LIMIT ?
                """,
                (player_id, game_type, limit),
            )
        else:
            cursor.execute(
                """
                SELECT gr.id, gr.game_type, gr.timestamp, gr.duration_ticks, gr.custom_data
                FROM game_results gr
                INNER JOIN game_result_players grp ON gr.id = grp.result_id
                WHERE grp.player_id = ?
                ORDER BY gr.timestamp DESC
                LIMIT ?
                """,
                (player_id, limit),
            )

        results = []
        for row in cursor.fetchall():
            results.append(
                {
                    "id": row["id"],
                    "game_type": row["game_type"],
                    "timestamp": row["timestamp"],
                    "duration_ticks": row["duration_ticks"],
                    "custom_data": json.loads(row["custom_data"]) if row["custom_data"] else {},
                }
            )
        return results

    def get_game_result_players(self, result_id: int) -> list[dict]:
        """Get all players for a specific game result."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            """
            SELECT player_id, player_name, is_bot, is_virtual_bot
            FROM game_result_players
            WHERE result_id = ?
            """,
            (result_id,),
        )
        return [
            {
                "player_id": row["player_id"],
                "player_name": row["player_name"],
                "is_bot": bool(row["is_bot"]),
                "is_virtual_bot": bool(row["is_virtual_bot"])
                if row["is_virtual_bot"] is not None
                else False,
            }
            for row in cursor.fetchall()
        ]

    def get_game_stats(self, game_type: str, limit: int | None = None) -> list[tuple]:
        """
        Get game results for a game type.

        Args:
            game_type: The game type to query
            limit: Optional maximum number of results

        Returns:
            List of tuples: (id, game_type, timestamp, duration_ticks, custom_data)
        """
        cursor = self._get_conn().cursor()

        if limit:
            cursor.execute(
                """
                SELECT id, game_type, timestamp, duration_ticks, custom_data
                FROM game_results
                WHERE game_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (game_type, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, game_type, timestamp, duration_ticks, custom_data
                FROM game_results
                WHERE game_type = ?
                ORDER BY timestamp DESC
                """,
                (game_type,),
            )

        return [
            (
                row["id"],
                row["game_type"],
                row["timestamp"],
                row["duration_ticks"],
                row["custom_data"],
            )
            for row in cursor.fetchall()
        ]

    def get_game_stats_aggregate(self, game_type: str) -> dict:
        """
        Get aggregate statistics for a game type.

        Returns:
            Dictionary with total_games, total_duration_ticks, etc.
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_games,
                SUM(duration_ticks) as total_duration,
                AVG(duration_ticks) as avg_duration
            FROM game_results
            WHERE game_type = ?
            """,
            (game_type,),
        )
        row = cursor.fetchone()
        return {
            "total_games": row["total_games"] or 0,
            "total_duration_ticks": row["total_duration"] or 0,
            "avg_duration_ticks": row["avg_duration"] or 0,
        }

    def get_player_stats(self, player_id: str, game_type: str | None = None) -> dict:
        """
        Get statistics for a player.

        Args:
            player_id: The player ID
            game_type: Optional filter by game type

        Returns:
            Dictionary with games_played, etc.
        """
        cursor = self._get_conn().cursor()

        if game_type:
            cursor.execute(
                """
                SELECT COUNT(*) as games_played
                FROM game_result_players grp
                INNER JOIN game_results gr ON grp.result_id = gr.id
                WHERE grp.player_id = ? AND gr.game_type = ?
                """,
                (player_id, game_type),
            )
        else:
            cursor.execute(
                """
                SELECT COUNT(*) as games_played
                FROM game_result_players
                WHERE player_id = ?
                """,
                (player_id,),
            )

        row = cursor.fetchone()
        return {
            "games_played": row["games_played"] or 0,
        }

    # Player rating operations

    def get_player_rating(self, player_id: str, game_type: str) -> tuple[float, float] | None:
        """
        Get a player's rating for a game type.

        Returns:
            (mu, sigma) tuple or None if no rating exists
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            """
            SELECT mu, sigma FROM player_ratings
            WHERE player_id = ? AND game_type = ?
            """,
            (player_id, game_type),
        )
        row = cursor.fetchone()
        if row:
            return (row["mu"], row["sigma"])
        return None

    def set_player_rating(self, player_id: str, game_type: str, mu: float, sigma: float) -> None:
        """Set or update a player's rating for a game type."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO player_ratings (player_id, game_type, mu, sigma)
            VALUES (?, ?, ?, ?)
            """,
            (player_id, game_type, mu, sigma),
        )
        self._get_conn().commit()

    def get_rating_leaderboard(
        self, game_type: str, limit: int = 10
    ) -> list[tuple[str, float, float]]:
        """
        Get the rating leaderboard for a game type.

        Returns:
            List of (player_id, mu, sigma) tuples sorted by mu descending
        """
        cursor = self._get_conn().cursor()
        cursor.execute(
            """
            SELECT player_id, mu, sigma FROM player_ratings
            WHERE game_type = ?
            ORDER BY mu DESC
            LIMIT ?
            """,
            (game_type, limit),
        )
        return [(row["player_id"], row["mu"], row["sigma"]) for row in cursor.fetchall()]

    # ==================== Virtual Bot Persistence ====================

    def _ensure_virtual_bots_table(self) -> None:
        """Create virtual_bots table if it doesn't exist."""
        cursor = self._get_conn().cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS virtual_bots (
                name TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                online_ticks INTEGER NOT NULL DEFAULT 0,
                target_online_ticks INTEGER NOT NULL DEFAULT 0,
                table_id TEXT,
                game_join_tick INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self._get_conn().commit()

    def save_virtual_bot(
        self,
        name: str,
        state: str,
        online_ticks: int,
        target_online_ticks: int,
        table_id: str | None,
        game_join_tick: int,
    ) -> None:
        """Save or update a virtual bot's state."""
        self._ensure_virtual_bots_table()
        cursor = self._get_conn().cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO virtual_bots
            (name, state, online_ticks, target_online_ticks, table_id, game_join_tick)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, state, online_ticks, target_online_ticks, table_id, game_join_tick),
        )
        self._get_conn().commit()

    def load_all_virtual_bots(self) -> list[dict]:
        """Load all virtual bot states from the database."""
        self._ensure_virtual_bots_table()
        cursor = self._get_conn().cursor()
        cursor.execute(
            """
            SELECT name, state, online_ticks, target_online_ticks, table_id, game_join_tick
            FROM virtual_bots
            """
        )
        return [
            {
                "name": row["name"],
                "state": row["state"],
                "online_ticks": row["online_ticks"],
                "target_online_ticks": row["target_online_ticks"],
                "table_id": row["table_id"],
                "game_join_tick": row["game_join_tick"],
            }
            for row in cursor.fetchall()
        ]

    def delete_virtual_bot(self, name: str) -> None:
        """Delete a single virtual bot from the database."""
        self._ensure_virtual_bots_table()
        cursor = self._get_conn().cursor()
        cursor.execute("DELETE FROM virtual_bots WHERE name = ?", (name,))
        self._get_conn().commit()

    def delete_all_virtual_bots(self) -> None:
        """Delete all virtual bots from the database."""
        self._ensure_virtual_bots_table()
        cursor = self._get_conn().cursor()
        cursor.execute("DELETE FROM virtual_bots")
        self._get_conn().commit()
