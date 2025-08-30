# HRM System - Singapore Human Resource Management

## Overview

A comprehensive Human Resource Management System specifically designed for Singapore companies with built-in compliance for CPF, AIS, and MOM OED regulations. The system provides a complete mobile-first solution for managing employees, payroll, attendance, leaves, claims, and performance appraisals while ensuring full compliance with Singapore labor laws.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Mobile-First Design**: Bootstrap-based responsive UI optimized for mobile devices with touch-friendly interfaces
- **Progressive Web App (PWA)**: Service worker support for offline functionality and app-like experience
- **Template Engine**: Jinja2 templates with modular component structure
- **JavaScript Framework**: Vanilla JavaScript with mobile optimizations and touch gesture support

### Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for rapid development and database abstraction
- **Application Structure**: Modular design with separate files for models, routes, authentication, and utilities
- **Authentication System**: Replit Auth integration with OAuth2 flow and role-based access control
- **Business Logic**: Specialized Singapore payroll calculation engine with CPF compliance

### Database Design
- **ORM**: SQLAlchemy with declarative base for model definitions
- **Core Models**: 
  - User/Employee management with role-based permissions (Admin, Manager, Employee)
  - Payroll system with Singapore-specific calculations
  - Attendance tracking with overtime calculations
  - Leave management with approval workflows
  - Claims processing with document attachments
  - Performance appraisal system
  - Compliance reporting for Singapore regulations
- **Data Integrity**: Foreign key relationships and unique constraints for data consistency

### Role-Based Access Control
- **Three-Tier System**: Admin (full access), Manager (team management), Employee (self-service)
- **Permission Decorators**: `@require_login` and `@require_role` for route protection
- **Contextual Access**: Users can only access data relevant to their role and scope

### Singapore Compliance Engine
- **CPF Calculator**: Automated CPF contribution calculations based on age, nationality, and employment status
- **AIS Integration**: Automated Income Supplement threshold tracking and reporting
- **MOM OED Filing**: Overseas Employee Data submission preparation
- **Bank Transfer Generation**: Automated payroll bank file generation for Singapore banks

## External Dependencies

### Authentication & Security
- **Replit Auth**: OAuth2-based authentication system integrated with Replit platform
- **Flask-Login**: Session management and user authentication state
- **Flask-Dance**: OAuth consumer integration for secure token handling

### Database & ORM
- **SQLAlchemy**: Database ORM with support for multiple database backends
- **Flask-SQLAlchemy**: Flask integration for SQLAlchemy with application context management
- **Database**: Environment-configurable database (PostgreSQL recommended for production)

### Frontend Libraries
- **Bootstrap**: Mobile-first CSS framework with dark theme support via Replit CDN
- **Font Awesome**: Icon library for consistent UI elements
- **Custom CSS**: Mobile optimization and PWA enhancements

### File Processing & Export
- **Pandas**: Data manipulation for complex payroll calculations and report generation
- **CSV Module**: Built-in Python module for data export functionality
- **BytesIO/StringIO**: In-memory file handling for report generation

### Compliance & Calculations
- **Decimal Module**: Precise financial calculations for payroll processing
- **Calendar Module**: Date calculations for payroll periods and working days
- **Singapore Payroll Calculator**: Custom engine for CPF, tax, and compliance calculations

### Development & Deployment
- **Werkzeug**: WSGI utilities and proxy fix for production deployment
- **Python Logging**: Comprehensive logging system for debugging and monitoring
- **Environment Variables**: Configuration management for database URLs and session secrets