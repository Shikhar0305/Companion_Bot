"""SSO + RBAC dependency (docs/02 §2.3, docs/09 §S2).

Placeholder that validates a bearer token and resolves a role. In production this
verifies the SSO/OIDC token and maps groups → roles
(officer|analyst|supervisor|admin). Disabled by default in the dev profile.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.config import get_settings


@dataclass
class Principal:
    user: str
    role: str


def authenticate(authorization: str | None) -> Principal:
    settings = get_settings()
    if not settings.auth_enabled:
        return Principal(user="dev", role="officer")
    # Production: verify SSO/OIDC bearer token here and map to a role.
    from fastapi import HTTPException

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1]
    principal = _verify_token(token)
    if principal is None:
        raise HTTPException(status_code=401, detail="invalid token")
    return principal


def _verify_token(token: str) -> Principal | None:
    # Stub: integrate the org IdP (Keycloak/OIDC) here.
    return None


def require_role(principal: Principal, *allowed: str) -> None:
    from fastapi import HTTPException

    if principal.role not in allowed:
        raise HTTPException(status_code=403, detail="insufficient role")
