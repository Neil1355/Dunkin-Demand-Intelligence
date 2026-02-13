"""
Email service for sending password reset and notification emails.

Supports multiple providers:
- SendGrid (recommended for production)
- Mailgun
- AWS SES
- Gmail SMTP (for testing only)

Installation:
pip install sendgrid
# or
pip install mailgun-python
# or
pip install boto3
"""

import os
from typing import Optional

# Choose your email provider
EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'sendgrid')  # sendgrid, mailgun, aws_ses, smtp


class EmailService:
    """Base email service."""
    
    @staticmethod
    def send_password_reset_email(recipient_email: str, reset_token: str, frontend_url: str) -> bool:
        """Send password reset email."""
        raise NotImplementedError


class SendGridService(EmailService):
    """SendGrid email service."""
    
    def __init__(self):
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            self.sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
            self.mail_class = Mail
        except ImportError:
            raise ImportError("sendgrid not installed. Run: pip install sendgrid")
    
    def send_password_reset_email(self, recipient_email: str, reset_token: str, frontend_url: str) -> bool:
        """Send password reset email via SendGrid."""
        try:
            reset_link = f"{frontend_url}/reset-password?token={reset_token}"
            
            message = self.mail_class(
                from_email=os.getenv('EMAIL_FROM', 'noreply@dunkindemand.com'),
                to_emails=recipient_email,
                subject='Reset Your Dunkin Demand Intelligence Password',
                html_content=self._get_html_template(reset_link)
            )
            
            self.sg.send(message)
            return True
        except Exception as e:
            print(f"SendGrid error: {e}")
            return False
    
    @staticmethod
    def _get_html_template(reset_link: str) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #FF671F 0%, #DA1884 100%); color: white; padding: 40px; border-radius: 12px; text-align: center;">
                    <h1>🍩 Dunkin Demand Intelligence</h1>
                    <p>Password Reset Request</p>
                </div>
                
                <div style="padding: 30px; background: #f5f0e8;">
                    <h2 style="color: #333;">Hi,</h2>
                    <p style="color: #666; line-height: 1.6;">
                        We received a request to reset your password. Click the button below to create a new password.
                    </p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="
                            display: inline-block;
                            background: #FF671F;
                            color: white;
                            padding: 12px 32px;
                            text-decoration: none;
                            border-radius: 24px;
                            font-weight: bold;
                        ">
                            Reset Password
                        </a>
                    </p>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 20px;">
                        Link expires in 1 hour. If you didn't request this, ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """


class MailgunService(EmailService):
    """Mailgun email service."""
    
    def __init__(self):
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("requests not installed. Run: pip install requests")
        
        self.domain = os.getenv('MAILGUN_DOMAIN')
        self.api_key = os.getenv('MAILGUN_API_KEY')
    
    def send_password_reset_email(self, recipient_email: str, reset_token: str, frontend_url: str) -> bool:
        """Send password reset email via Mailgun."""
        try:
            reset_link = f"{frontend_url}/reset-password?token={reset_token}"
            
            data = {
                "from": f"Dunkin DDI <noreply@{self.domain}>",
                "to": recipient_email,
                "subject": "Reset Your Dunkin Demand Intelligence Password",
                "html": SendGridService._get_html_template(reset_link)
            }
            
            response = self.requests.post(
                f"https://api.mailgun.net/v3/{self.domain}/messages",
                auth=("api", self.api_key),
                data=data
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Mailgun error: {e}")
            return False


def send_password_reset_email(recipient_email: str, reset_token: str, frontend_url: str) -> bool:
    """Send password reset email using configured provider."""
    
    if EMAIL_PROVIDER == 'sendgrid':
        service = SendGridService()
    elif EMAIL_PROVIDER == 'mailgun':
        service = MailgunService()
    else:
        print(f"Email provider '{EMAIL_PROVIDER}' not supported for production")
        return False
    
    return service.send_password_reset_email(recipient_email, reset_token, frontend_url)
