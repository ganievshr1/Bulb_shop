from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from app import models
from app.utils import serialize_for_audit


class AuditService:
    @staticmethod
    async def log_action(
            db: Session,
            admin_id: int,
            action: str,
            entity_type: str,
            entity_id: Optional[int] = None,
            old_value: Optional[Any] = None,
            new_value: Optional[Any] = None,
            ip_address: Optional[str] = None,
            user_agent: Optional[str] = None
    ) -> models.AuditLog:
        """Log admin action to audit trail"""
        audit_log = models.AuditLog(
            admin_id=admin_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=serialize_for_audit(old_value),
            new_value=serialize_for_audit(new_value),
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

    @staticmethod
    def get_logs(
            db: Session,
            page: int = 1,
            limit: int = 50,
            admin_id: Optional[int] = None,
            action: Optional[str] = None,
            entity_type: Optional[str] = None,
            entity_id: Optional[int] = None,
            from_date: Optional[str] = None,
            to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get filtered audit logs"""
        query = db.query(models.AuditLog)

        # Apply filters
        if admin_id:
            query = query.filter(models.AuditLog.admin_id == admin_id)
        if action:
            query = query.filter(models.AuditLog.action == action)
        if entity_type:
            query = query.filter(models.AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(models.AuditLog.entity_id == entity_id)
        if from_date:
            query = query.filter(models.AuditLog.created_at >= datetime.fromisoformat(from_date))
        if to_date:
            query = query.filter(models.AuditLog.created_at <= datetime.fromisoformat(to_date))

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        offset = (page - 1) * limit
        logs = query.order_by(models.AuditLog.created_at.desc()).offset(offset).limit(limit).all()

        # Enrich with admin names
        result_logs = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "admin_id": log.admin_id,
                "admin_name": None,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "created_at": log.created_at
            }

            # Get admin name if admin exists
            if log.admin_id:
                admin = db.query(models.Admin).filter(models.Admin.id == log.admin_id).first()
                if admin:
                    log_dict["admin_name"] = admin.full_name

            result_logs.append(log_dict)

        return {
            "logs": result_logs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1
            }
        }

    @staticmethod
    def get_entity_history(
            db: Session,
            entity_type: str,
            entity_id: int,
            page: int = 1,
            limit: int = 50
    ) -> Dict[str, Any]:
        """Get change history for a specific entity"""
        query = db.query(models.AuditLog).filter(
            models.AuditLog.entity_type == entity_type,
            models.AuditLog.entity_id == entity_id
        )

        total = query.count()
        offset = (page - 1) * limit
        logs = query.order_by(models.AuditLog.created_at.desc()).offset(offset).limit(limit).all()

        result_logs = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "action": log.action,
                "admin_name": None,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "created_at": log.created_at
            }

            if log.admin_id:
                admin = db.query(models.Admin).filter(models.Admin.id == log.admin_id).first()
                if admin:
                    log_dict["admin_name"] = admin.full_name

            result_logs.append(log_dict)

        return {
            "logs": result_logs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1
            }
        }

    @staticmethod
    def get_stats(db: Session) -> Dict[str, Any]:
        """Get audit statistics"""
        # Total actions count
        total_actions = db.query(func.count(models.AuditLog.id)).scalar()

        # Actions by type
        actions_by_type = db.query(
            models.AuditLog.action,
            func.count(models.AuditLog.id)
        ).group_by(models.AuditLog.action).all()

        # Actions by entity
        actions_by_entity = db.query(
            models.AuditLog.entity_type,
            func.count(models.AuditLog.id)
        ).group_by(models.AuditLog.entity_type).all()

        # Actions by admin
        actions_by_admin = db.query(
            models.Admin.login,
            func.count(models.AuditLog.id)
        ).join(models.AuditLog, models.Admin.id == models.AuditLog.admin_id) \
            .group_by(models.Admin.login).all()

        return {
            "total_actions": total_actions,
            "by_action": [{"action": a, "count": c} for a, c in actions_by_type],
            "by_entity": [{"entity": e, "count": c} for e, c in actions_by_entity],
            "by_admin": [{"admin": a, "count": c} for a, c in actions_by_admin]
        }