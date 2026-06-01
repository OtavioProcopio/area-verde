import base64
import hashlib
import hmac
import secrets

PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_DIGEST = "sha256"
PBKDF2_ITERATIONS = 600000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        PBKDF2_DIGEST,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    encoded = base64.b64encode(digest).decode("utf-8")
    return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt}${encoded}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False

    try:
        algorithm, iterations, salt, encoded = stored_hash.split("$", 3)
        if algorithm != PBKDF2_ALGORITHM:
            return False

        digest = hashlib.pbkdf2_hmac(
            PBKDF2_DIGEST,
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )
        candidate = base64.b64encode(digest).decode("utf-8")
        return hmac.compare_digest(candidate, encoded)
    except (TypeError, ValueError):
        return False
