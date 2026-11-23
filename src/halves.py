"""Observer halves.

An observer is locked if the SHA-256 digest of the ASCII text "IG8-half:"
followed by the decimal observer_id, read as an integer, is odd; the observer
belongs to the development half otherwise. Outcomes of locked observers are
used only in a registered confirmatory decision of docs/PLAN.md.
"""
import hashlib

PREFIX = "IG8-half:"


def is_locked(observer_id: int) -> bool:
    """True if the observer belongs to the locked half."""
    digest = hashlib.sha256((PREFIX + str(int(observer_id))).encode("ascii")).hexdigest()
    return int(digest, 16) % 2 == 1


if __name__ == "__main__":
    # Small self-check: the rule is deterministic and splits ids into two halves.
    ids = range(1, 100001)
    locked = sum(is_locked(i) for i in ids)
    assert is_locked(12345) == is_locked(12345)
    print(f"locked share among ids 1..100000: {locked / 100000:.4f}")
