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
        Send an email using the tenant's SMTP or AWS configuration.
        """
        try:
            config = EmailConfig.query.filter_by(tenant_id=tenant_id, is_active=True).first()
            
            provider = config.provider if config else 'SMTP'
            
            if provider == 'AWS_SES':
                return EmailService._send_via_aws_ses(config, recipient, subject, body, is_html, attachments)
            elif provider == 'AWS_SNS':
                return EmailService._send_via_aws_sns(config, recipient, subject, body)
            
            # Default SMTP logic
            return EmailService._send_via_smtp(tenant_id, config, recipient, subject, body, is_html, attachments)

        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")
            EmailService.log_email(tenant_id, recipient, subject, 'Failed', str(e))
            return False, str(e)

    @staticmethod
    def _send_via_smtp(tenant_id, config, recipient, subject, body, is_html, attachments):
        smtp_host = config.smtp_host if config else current_app.config.get('MAIL_SERVER')
        smtp_port = config.smtp_port if config else current_app.config.get('MAIL_PORT')
        smtp_user = config.smtp_user if config else current_app.config.get('MAIL_USERNAME')
        smtp_password = config.smtp_password if config else current_app.config.get('MAIL_PASSWORD')
        from_email = config.from_email if config else current_app.config.get('MAIL_DEFAULT_SENDER')
        use_tls = config.use_tls if config else current_app.config.get('MAIL_USE_TLS', True)
        use_ssl = config.use_ssl if config else current_app.config.get('MAIL_USE_SSL', False)

        if not smtp_host or not from_email:
            raise Exception("No SMTP configuration found for tenant or system.")

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

        if attachments:
            from email.mime.base import MIMEBase
            from email import encoders
            for att in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(att['data'])
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {att['filename']}")
                msg.attach(part)

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
        
        EmailService.log_email(tenant_id, recipient, subject, 'Sent')
        return True, "Email sent successfully"

    @staticmethod
    def _send_via_aws_ses(config, recipient, subject, body, is_html, attachments):
        import boto3
        from botocore.exceptions import ClientError
        
        # Prefer DB config, fallback to environment
        aws_key = config.aws_access_key or current_app.config.get('AWS_ACCESS_KEY_ID')
        aws_secret = config.aws_secret_key or current_app.config.get('AWS_SECRET_ACCESS_KEY')
        aws_region = config.aws_region or current_app.config.get('AWS_REGION')

        client = boto3.client(
            'ses',
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region
        )

        source = config.from_email
        if config.from_name:
            source = f"{config.from_name} <{config.from_email}>"

        if attachments:
            # SES requires raw email for attachments
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = source
            msg['To'] = recipient
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            from email.mime.base import MIMEBase
            from email import encoders
            for att in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(att['data'])
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {att['filename']}")
                msg.attach(part)
                
            response = client.send_raw_email(
                Source=source,
                Destinations=[recipient],
                RawMessage={'Data': msg.as_string()}
            )
        else:
            response = client.send_email(
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Body': {
                        'Html': {'Charset': 'UTF-8', 'Data': body} if is_html else {'Charset': 'UTF-8', 'Data': body},
                        'Text': {'Charset': 'UTF-8', 'Data': body} if not is_html else {'Charset': 'UTF-8', 'Data': body}
                    },
                    'Subject': {'Charset': 'UTF-8', 'Data': subject},
                },
                Source=source
            )
        
        EmailService.log_email(config.tenant_id, recipient, subject, 'Sent')
        return True, "Email sent via AWS SES"

    @staticmethod
    def _send_via_aws_sns(config, recipient, subject, body):
        import boto3
        
        # Prefer DB config, fallback to environment
        aws_key = config.aws_access_key or current_app.config.get('AWS_ACCESS_KEY_ID')
        aws_secret = config.aws_secret_key or current_app.config.get('AWS_SECRET_ACCESS_KEY')
        aws_region = config.aws_region or current_app.config.get('AWS_REGION')

        client = boto3.client(
            'sns',
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region
        )
        
        if config.aws_topic_arn:
            # Publish to Topic
            client.publish(
                TopicArn=config.aws_topic_arn,
                Message=body,
                Subject=subject
            )
        else:
            # Direct to Email (Note: This usually requires the email to be AWS-verified if using SES-backed SNS)
            # Actually SNS publish doesn't take 'ToAddress' for emails directly easily without a topic
            # But we can publish to a phone number or use it for general notifications.
            # If it's a "Report", publishing to a Topic is more appropriate.
            raise Exception("AWS SNS requires a Topic ARN for report delivery.")

        EmailService.log_email(config.tenant_id, recipient, subject, 'Sent')
        return True, "Notification sent via AWS SNS"

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
