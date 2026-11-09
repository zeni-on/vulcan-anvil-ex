"""Delivery profile identity shared by the CLI, process and release policies."""

import json
from pathlib import Path


DEFAULT_DELIVERY_PROFILE = "audit"
SUPPORTED_DELIVERY_PROFILES = ("audit", "product")
DELIVERY_PROFILE_ALIASES = {"solution": "product"}


class UnsupportedProfile(ValueError):
    pass


def normalize_delivery_profile(profile):
    if profile is None or profile == "":
        return DEFAULT_DELIVERY_PROFILE
    name = str(profile).strip().lower()
    name = DELIVERY_PROFILE_ALIASES.get(name, name)
    if name not in SUPPORTED_DELIVERY_PROFILES:
        reason = ("retired (지원 중단)" if name in {"poc", "proof-of-concept", "proof_of_concept", "proof of concept"}
                  else "unsupported (지원하지 않음)")
        raise UnsupportedProfile(
            f"Delivery profile {profile!r}: {reason}. Supported: audit, product. "
            "No automatic conversion; existing project files must be preserved."
        )
    return name


def declared_profile(record, keys=("profile", "delivery_profile")):
    """Validate both spellings even when a higher-priority one is present."""
    selected = None
    for key in keys:
        raw = record.get(key)
        if raw is not None and raw != "":
            value = normalize_delivery_profile(raw)
            selected = selected or value
    return selected


def load_delivery_profile(project_dir="."):
    selected = None
    for name, keys in (("session.json", ("profile", "delivery_profile")),
                       ("vulcan.config.json", ("delivery_profile", "profile"))):
        path = Path(project_dir) / name
        try:
            with path.open(encoding="utf-8-sig") as stream:
                record = json.load(stream)
        except FileNotFoundError:
            continue
        except (OSError, ValueError) as error:
            raise UnsupportedProfile(f"Cannot verify delivery profile in {path}: {error}") from error
        if not isinstance(record, dict):
            raise UnsupportedProfile(f"Cannot verify delivery profile in {path}: expected an object")
        try:
            value = declared_profile(record, keys)
        except UnsupportedProfile as error:
            raise UnsupportedProfile(f"{path}: {error}") from error
        selected = selected or value
    return selected or DEFAULT_DELIVERY_PROFILE
