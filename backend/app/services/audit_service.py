
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def create_audit_log(
    db: Session,
    action: str,
    status: str,
    user_id: int | None = None,
    endpoint: str | None = None,
    details: dict[str, Any] | str | None = None,
) -> AuditLog:
    """
    Create an audit log entry.

    Call this function from API endpoints or services
    after an important action.
    """

    if isinstance(details, dict):
        details_text = json.dumps(
            details,
            default=str
        )
    else:
        details_text = details

    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        endpoint=endpoint,
        status=status,
        details=details_text,
    )

    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)

    return audit_entry
