import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import current_app
from core.models import EmailConfig, EmailLog, db

class EmailService:
    @staticmethod
    def send_email(tenant_id, recipient, subject, body, is_html=True, attachments=None):
        """
        Send an email using the tenant's SMTP configuration.
        Falls back to system configuration if tenant config is missing.
        """
        try:
            # 1. Get Tenant Config
            config = EmailConfig.query.filter_by(tenant_id=tenant_id, is_active=True).first()
            
            smtp_host = None
            smtp_port = None
            smtp_user = None
            smtp_password = None
            from_email = None
            use_tls = True
            use_ssl = False

            if config:
                smtp_host = config.smtp_host
                smtp_port = config.smtp_port
                smtp_user = config.smtp_user
                smtp_password = config.smtp_password
                from_email = config.from_email
                use_tls = config.use_tls
                use_ssl = config.use_ssl
            else:
                # Fallback to system env vars
                smtp_host = current_app.config.get('MAIL_SERVER')
                smtp_port = current_app.config.get('MAIL_PORT')
                smtp_user = current_app.config.get('MAIL_USERNAME')
                smtp_password = current_app.config.get('MAIL_PASSWORD')
                from_email = current_app.config.get('MAIL_DEFAULT_SENDER')
                use_tls = current_app.config.get('MAIL_USE_TLS', True)
                use_ssl = current_app.config.get('MAIL_USE_SSL', False)
            
            if not smtp_host or not from_email:
                raise Exception("No SMTP configuration found for tenant or system.")

            # 2. Construct Message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            # Handle attachments if any (list of dicts {filename, data, content_type})
            if attachments:
                from email.mime.base import MIMEBase
                from email import encoders
                for att in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(att['data'])
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename= {att['filename']}")
                    msg.attach(part)

            # 3. Connect and Send
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port)
                if use_tls:
                    server.starttls()
            
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
                
            server.sendmail(from_email, recipient, msg.as_string())
            server.quit()
            
            # 4. Log Success
            EmailService.log_email(tenant_id, recipient, subject, 'Sent')
            return True, "Email sent successfully"

        except Exception as e:
            # 5. Log Failure
            current_app.logger.error(f"Failed to send email: {str(e)}")
            EmailService.log_email(tenant_id, recipient, subject, 'Failed', str(e))
            return False, str(e)

    @staticmethod
    def log_email(tenant_id, recipient, subject, status, error_message=None):
        try:
            log = EmailLog(
                tenant_id=tenant_id,
                recipient=recipient,
                subject=subject,
                status=status,
                error_message=error_message,
                sent_at=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to log email: {str(e)}")
