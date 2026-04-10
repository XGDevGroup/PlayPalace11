"""Authentication and session management."""

import hashlib
import secrets
import time
from enum import Enum, auto
from typing import TYPE_CHECKING

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from server.core.users.base import TrustLevel


class AuthResult(Enum):
    """Result of an authentication attempt."""

    SUCCESS = auto()
    USER_NOT_FOUND = auto()
    WRONG_PASSWORD = auto()


if TYPE_CHECKING:
    from ..persistence.database import Database, UserRecord


class AuthManager:
    """Handle user authentication and session management.

    Uses Argon2 for password hashing and supports migration from legacy
    SHA-256 hashes on successful login.
    """

    def __init__(self, database: "Database"):
        """Initialize the auth manager with a database backend."""
        self._db = database
        self._sessions: dict[str, tuple[str, int]] = {}  # token -> (username, expires_at)
        self._hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2."""
        return self._hasher.hash(password)

    def _hash_password_sha256(self, password: str) -> str:
        """Legacy SHA-256 hash for migration support."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _is_legacy_hash(self, password_hash: str) -> bool:
        """Check if a hash is a legacy SHA-256 hash (64 hex characters)."""
        return len(password_hash) == 64 and all(
            c in "0123456789abcdef" for c in password_hash.lower()
        )

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash (supports both Argon2 and legacy SHA-256)."""
        # Try Argon2 first
        try:
            self._hasher.verify(password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHashError):
            pass

        # Fall back to SHA-256 for legacy hashes
        if self._is_legacy_hash(password_hash):
            return self._hash_password_sha256(password) == password_hash

        return False

    def authenticate(self, username: str, password: str) -> AuthResult:
        """Authenticate a user.

        Args:
            username: Username to authenticate.
            password: Plaintext password to verify.

        Returns:
            AuthResult indicating success or failure reason.
        """
        user = self._db.get_user(username)
        if not user:
            return AuthResult.USER_NOT_FOUND

        if not self.verify_password(password, user.password_hash):
            return AuthResult.WRONG_PASSWORD

        # Upgrade legacy hash to Argon2 on successful login
        if self._is_legacy_hash(user.password_hash):
            new_hash = self.hash_password(password)
            self._db.update_user_password(username, new_hash)

        return AuthResult.SUCCESS

    def register(self, username: str, password: str, *, approved: bool = False, locale: str = "en") -> bool:
        """Register a new user.

        Args:
            username: Username to create.
            password: Plaintext password.
            approved: Whether the account is pre-approved (skips admin approval).
            locale: Preferred locale.

        Returns:
            True if registration succeeded, False if username taken.
        """
        if self._db.user_exists(username):
            return False

        trust_level = TrustLevel.USER

        password_hash = self.hash_password(password)
        self._db.create_user(username, password_hash, locale, trust_level, approved)

        return True

    def reset_password(self, username: str, new_password: str) -> bool:
        """Reset a user's password.

        Args:
            username: Username to update.
            new_password: New plaintext password.

        Returns:
            True if successful, False if user doesn't exist.
        """
        if not self._db.user_exists(username):
            return False

        password_hash = self.hash_password(new_password)
        self._db.update_user_password(username, password_hash)
        return True

    def get_user(self, username: str) -> "UserRecord | None":
        """Get a user record."""
        return self._db.get_user(username)

    def create_session(self, username: str, ttl_seconds: int) -> tuple[str, int]:
        """Create an access session token for a user.

        Returns:
            (token, expires_at_epoch_seconds)
        """
        token = secrets.token_hex(32)
        expires_at = int(time.time()) + ttl_seconds
        self._sessions[token] = (username, expires_at)
        return token, expires_at

    def validate_session(self, token: str) -> str | None:
        """Validate an access session token."""
        entry = self._sessions.get(token)
        if not entry:
            return None
        username, expires_at = entry
        if expires_at <= int(time.time()):
            self._sessions.pop(token, None)
            return None
        return username

    def invalidate_session(self, token: str) -> None:
        """Invalidate a session token.

        Args:
            token: Session token string.
        """
        self._sessions.pop(token, None)

    def invalidate_user_sessions(self, username: str) -> None:
        """Invalidate all sessions for a user.

        Args:
            username: Username whose sessions should be invalidated.
        """
        to_remove = [t for t, (u, _expires_at) in self._sessions.items() if u == username]
        for token in to_remove:
            del self._sessions[token]

    def create_refresh_token(self, username: str, ttl_seconds: int) -> tuple[str, int]:
        """Create and persist a refresh token."""
        token = secrets.token_hex(32)
        now = int(time.time())
        expires_at = now + ttl_seconds
        self._db.store_refresh_token(username, token, expires_at, now)
        return token, expires_at

    def refresh_session(
        self, refresh_token: str, access_ttl_seconds: int, refresh_ttl_seconds: int
    ) -> tuple[str, str, int, str, int] | None:
        """Rotate refresh token and issue a new access token.

        Returns:
            (username, access_token, access_expires_at, refresh_token, refresh_expires_at)
        """
        record = self._db.get_refresh_token(refresh_token)
        if not record:
            return None

        username = record.username
        if not self._db.user_exists(username):
            return None

        now = int(time.time())
        if record.revoked_at is not None or record.replaced_by:
            return None
        if record.expires_at <= now:
            self._db.revoke_refresh_token(refresh_token, now)
            return None

        new_refresh_token = secrets.token_hex(32)
        new_refresh_expires = now + refresh_ttl_seconds
        self._db.store_refresh_token(username, new_refresh_token, new_refresh_expires, now)
        self._db.revoke_refresh_token(refresh_token, now, replaced_by=new_refresh_token)

        access_token, access_expires = self.create_session(username, access_ttl_seconds)
        return username, access_token, access_expires, new_refresh_token, new_refresh_expires
