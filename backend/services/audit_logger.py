"""
Audit logging service for tracking user actions
Logs all significant actions (login, data changes, exports, etc.)
"""

from models.db import get_connection, return_connection
from datetime import datetime
from flask import request
import os

class AuditLogger:
    """Logs user actions to audit_log table for security and compliance"""
    
    ACTION_TYPES = {
        'login': 'User login',
        'logout': 'User logout',
        'login_failed': 'Failed login attempt',
        'password_reset_requested': 'Password reset requested',
        'password_reset_completed': 'Password reset completed',
        'user_created': 'New user created',
        'user_deleted': 'User deleted',
        'data_exported': 'Data exported to Excel',
        'forecast_approved': 'Forecast approved',
        'forecast_edited': 'Forecast edited',
        'waste_submitted': 'Waste data submitted',
        'qr_code_created': 'QR code created',
        'qr_code_downloaded': 'QR code downloaded',
        'qr_code_scanned': 'QR code scanned',
        'settings_changed': 'Settings changed',
        'permission_denied': 'Permission denied',
        'suspicious_activity': 'Suspicious activity detected',
    }
    
    @staticmethod
    def log(
        user_id: int = None,
        action_type: str = 'unknown',
        resource_type: str = None,
        resource_id: int = None,
        details: dict = None,
        status: str = 'success'
    ):
        """
        Log an action to database
        
        Args:
            user_id: ID of user performing action (optional)
            action_type: Type of action from ACTION_TYPES
            resource_type: Type of resource affected (user, forecast, waste, etc.)
            resource_id: ID of affected resource
            details: Additional JSON details
            status: 'success', 'failure', 'warning'
        """
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                ip_address = request.remote_addr if request else None
                user_agent = request.headers.get('User-Agent', '') if request else ''
                
                cur.execute('''
                    INSERT INTO audit_log (
                        user_id, action_type, resource_type, resource_id, 
                        ip_address, user_agent, details, status, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ''', (
                    user_id,
                    action_type,
                    resource_type,
                    resource_id,
                    ip_address,
                    user_agent,
                    details,
                    status
                ))
                conn.commit()
        except Exception as e:
            print(f"Error logging audit action: {e}")
        finally:
            if conn:
                return_connection(conn)
    
    @staticmethod
    def log_login(user_id: int, success: bool = True):
        """Log login attempt"""
        AuditLogger.log(
            user_id=user_id,
            action_type='login' if success else 'login_failed',
            resource_type='auth',
            status='success' if success else 'failure'
        )
    
    @staticmethod
    def log_password_reset(user_id: int, stage: str):
        """Log password reset stages"""
        action_map = {
            'requested': 'password_reset_requested',
            'completed': 'password_reset_completed',
        }
        AuditLogger.log(
            user_id=user_id,
            action_type=action_map.get(stage, 'password_reset_requested'),
            resource_type='auth'
        )
    
    @staticmethod
    def log_data_export(user_id: int, export_type: str):
        """Log data export"""
        AuditLogger.log(
            user_id=user_id,
            action_type='data_exported',
            resource_type='export',
            details={'export_type': export_type}
        )
    
    @staticmethod
    def log_waste_submission(user_id: int, store_id: int, waste_count: int):
        """Log waste submission"""
        AuditLogger.log(
            user_id=user_id,
            action_type='waste_submitted',
            resource_type='waste',
            resource_id=store_id,
            details={'waste_count': waste_count}
        )
    
    @staticmethod
    def log_qr_action(store_id: int, action: str, user_id: int = None):
        """Log QR code related actions"""
        AuditLogger.log(
            user_id=user_id,
            action_type=f'qr_code_{action}',
            resource_type='qr_code',
            resource_id=store_id
        )
    
    @staticmethod
    def log_suspicious_activity(user_id: int = None, reason: str = None):
        """Log suspicious activity for security review"""
        AuditLogger.log(
            user_id=user_id,
            action_type='suspicious_activity',
            details={'reason': reason},
            status='warning'
        )
    
    @staticmethod
    def get_user_activity(user_id: int, limit: int = 50):
        """Get recent activity for a user"""
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT id, action_type, resource_type, resource_id, 
                           status, created_at, ip_address
                    FROM audit_log
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                ''', (user_id, limit))
                rows = cur.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching user activity: {e}")
            return []
        finally:
            if conn:
                return_connection(conn)
    
    @staticmethod
    def get_recent_activity(limit: int = 100, action_type: str = None, user_id: int = None):
        """Get recent activity across system"""
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                query = 'SELECT * FROM audit_log WHERE 1=1'
                params = []
                
                if action_type:
                    query += ' AND action_type = %s'
                    params.append(action_type)
                
                if user_id:
                    query += ' AND user_id = %s'
                    params.append(user_id)
                
                query += ' ORDER BY created_at DESC LIMIT %s'
                params.append(limit)
                
                cur.execute(query, params)
                rows = cur.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching recent activity: {e}")
            return []
        finally:
            if conn:
                return_connection(conn)


# Global audit logger instance
audit_log = AuditLogger()
