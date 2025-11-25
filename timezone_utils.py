"""
Timezone utility functions for company-level timezone management

This module provides functions to:
1. Convert UTC times to company timezone for display
2. Convert local times to UTC for storage
3. Get timezone-aware datetime objects
4. List available timezones
"""

from datetime import datetime, timezone as tz_module
import pytz
from flask import current_app


# List of common IANA timezone identifiers
SUPPORTED_TIMEZONES = [
    'UTC',
    'Asia/Singapore',
    'Asia/Hong_Kong',
    'Asia/Tokyo',
    'Asia/Bangkok',
    'Asia/Manila',
    'Asia/Jakarta',
    'Asia/Kolkata',
    'Asia/Dubai',
    'America/New_York',
    'America/Chicago',
    'America/Los_Angeles',
    'America/Denver',
    'America/Toronto',
    'Europe/London',
    'Europe/Paris',
    'Europe/Berlin',
    'Europe/Amsterdam',
    'Europe/Istanbul',
    'Australia/Sydney',
    'Australia/Melbourne',
    'Pacific/Auckland',
    'Pacific/Fiji',
]

# Full list of all available IANA timezones (can be extended with pytz.all_timezones)
def get_all_timezones():
    """Get all available IANA timezones"""
    return sorted(pytz.all_timezones)


def get_company_timezone(company):
    """
    Get the timezone for a company
    
    Args:
        company: Company model instance
        
    Returns:
        str: Timezone identifier (e.g., 'Asia/Singapore')
    """
    if company and company.timezone:
        return company.timezone
    return 'UTC'


def get_timezone_object(timezone_str):
    """
    Get a pytz timezone object from timezone string
    
    Args:
        timezone_str: Timezone identifier (e.g., 'Asia/Singapore')
        
    Returns:
        pytz.timezone object or UTC if invalid
    """
    try:
        return pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        return pytz.UTC


def convert_utc_to_company_timezone(utc_datetime, company):
    """
    Convert a UTC datetime to company's local timezone
    
    Args:
        utc_datetime: datetime object in UTC (should be naive or UTC-aware)
        company: Company model instance
        
    Returns:
        datetime: localized datetime in company timezone, or None if input is None
    """
    if utc_datetime is None:
        return None
    
    company_tz = get_company_timezone(company)
    tz = get_timezone_object(company_tz)
    
    # If datetime is naive, assume it's UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = pytz.UTC.localize(utc_datetime)
    # If datetime is already timezone-aware but not UTC, convert to UTC first
    elif utc_datetime.tzinfo != pytz.UTC:
        utc_datetime = utc_datetime.astimezone(pytz.UTC)
    
    # Convert to company timezone
    return utc_datetime.astimezone(tz)


def convert_company_timezone_to_utc(local_datetime, company):
    """
    Convert a local datetime in company timezone to UTC
    
    Args:
        local_datetime: datetime object in company's local timezone (should be naive)
        company: Company model instance
        
    Returns:
        datetime: UTC datetime, or None if input is None
    """
    if local_datetime is None:
        return None
    
    company_tz = get_company_timezone(company)
    tz = get_timezone_object(company_tz)
    
    # If datetime is naive, localize it to company timezone
    if local_datetime.tzinfo is None:
        local_datetime = tz.localize(local_datetime)
    
    # Convert to UTC
    return local_datetime.astimezone(pytz.UTC).replace(tzinfo=None)


def get_current_time_in_company_timezone(company):
    """
    Get current time in company's timezone
    
    Args:
        company: Company model instance
        
    Returns:
        datetime: Current time in company's timezone
    """
    utc_now = datetime.now(pytz.UTC)
    return convert_utc_to_company_timezone(utc_now, company)


def format_time_for_display(datetime_obj, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Format a datetime object for display
    
    Args:
        datetime_obj: datetime object
        format_str: format string for strftime
        
    Returns:
        str: formatted datetime string
    """
    if datetime_obj is None:
        return ""
    
    try:
        return datetime_obj.strftime(format_str)
    except:
        return str(datetime_obj)


def get_timezone_offset_str(company):
    """
    Get timezone offset string for display (e.g., '+08:00', '-05:00')
    
    Args:
        company: Company model instance
        
    Returns:
        str: timezone offset
    """
    tz = get_timezone_object(get_company_timezone(company))
    now = datetime.now(tz)
    offset = now.strftime('%z')
    if offset:
        return f"{offset[:3]}:{offset[3:]}"
    return '+00:00'


def validate_timezone(timezone_str):
    """
    Validate if a timezone string is valid
    
    Args:
        timezone_str: Timezone identifier
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        pytz.timezone(timezone_str)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False