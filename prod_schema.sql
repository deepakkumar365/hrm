--
-- PostgreSQL database dump
--

-- Dumped from database version 17.7 (Debian 17.7-3.pgdg12+1)
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: attendance_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.attendance_status_enum AS ENUM (
    'Present',
    'Incomplete',
    'Absent',
    'Leave',
    'Half Day',
    'Weekly Off',
    'Holiday',
    'On Duty'
);


--
-- Name: update_modified_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_modified_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: hrm_appraisal; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_appraisal (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    review_period_start date NOT NULL,
    review_period_end date NOT NULL,
    performance_rating integer,
    goals_achievement integer,
    teamwork_rating integer,
    communication_rating integer,
    overall_rating numeric(3,2),
    self_review text,
    manager_feedback text,
    development_goals text,
    training_recommendations text,
    status character varying(20),
    reviewed_by integer,
    completed_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: hrm_appraisal_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_appraisal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_appraisal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_appraisal_id_seq OWNED BY public.hrm_appraisal.id;


--
-- Name: hrm_attendance; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_attendance (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    date date NOT NULL,
    clock_in time without time zone,
    clock_out time without time zone,
    break_start time without time zone,
    break_end time without time zone,
    regular_hours numeric(5,2),
    overtime_hours numeric(5,2),
    total_hours numeric(5,2),
    status public.attendance_status_enum,
    remarks text,
    location_lat character varying(20),
    location_lng character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    has_overtime boolean DEFAULT false,
    overtime_approved boolean,
    overtime_approved_by integer,
    overtime_approved_at timestamp without time zone,
    lop boolean DEFAULT false,
    timezone character varying(50) DEFAULT 'UTC'::character varying,
    clock_in_time timestamp without time zone,
    clock_out_time timestamp without time zone,
    sub_status character varying(50),
    leave_id integer,
    regularization_id integer,
    is_late boolean,
    is_early_departure boolean,
    late_minutes integer,
    early_departure_minutes integer
);


--
-- Name: hrm_attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_attendance_id_seq OWNED BY public.hrm_attendance.id;


--
-- Name: hrm_attendance_regularization; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_attendance_regularization (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    date date NOT NULL,
    original_clock_in timestamp without time zone,
    original_clock_out timestamp without time zone,
    corrected_clock_in timestamp without time zone NOT NULL,
    corrected_clock_out timestamp without time zone NOT NULL,
    reason text,
    proof_path character varying(255),
    status character varying(20),
    requested_by integer,
    approved_by integer,
    approved_at timestamp without time zone,
    rejection_reason text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: hrm_attendance_regularization_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_attendance_regularization_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_attendance_regularization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_attendance_regularization_id_seq OWNED BY public.hrm_attendance_regularization.id;


--
-- Name: hrm_attendance_segments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_attendance_segments (
    id integer NOT NULL,
    attendance_id integer NOT NULL,
    segment_type character varying(20),
    clock_in timestamp without time zone NOT NULL,
    clock_out timestamp without time zone,
    duration_minutes integer,
    location_lat character varying(20),
    location_lng character varying(20),
    remarks text,
    created_at timestamp without time zone
);


--
-- Name: hrm_attendance_segments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_attendance_segments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_attendance_segments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_attendance_segments_id_seq OWNED BY public.hrm_attendance_segments.id;


--
-- Name: hrm_audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_audit_log (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    resource_type character varying(100) NOT NULL,
    resource_id character varying(100) NOT NULL,
    changes text,
    status character varying(20),
    created_at timestamp without time zone NOT NULL
);


--
-- Name: hrm_audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_audit_log_id_seq OWNED BY public.hrm_audit_log.id;


--
-- Name: hrm_claim; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_claim (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    claim_type character varying(30) NOT NULL,
    amount numeric(10,2) NOT NULL,
    claim_date date NOT NULL,
    description text,
    receipt_number character varying(50),
    status character varying(20),
    submitted_by integer,
    approved_by integer,
    approved_at timestamp without time zone,
    rejection_reason text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: hrm_claim_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_claim_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_claim_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_claim_id_seq OWNED BY public.hrm_claim.id;


--
-- Name: hrm_company; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_company (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    address text,
    uen character varying(50),
    registration_number character varying(100),
    tax_id character varying(50),
    phone character varying(20),
    email character varying(255),
    website character varying(255),
    logo_path character varying(255),
    is_active boolean DEFAULT true NOT NULL,
    created_by character varying(100) DEFAULT 'system'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone,
    currency_code character varying(10) NOT NULL,
    timezone character varying(50) NOT NULL,
    CONSTRAINT chk_company_code_not_empty CHECK ((length(TRIM(BOTH FROM code)) > 0)),
    CONSTRAINT chk_company_name_not_empty CHECK ((length(TRIM(BOTH FROM name)) > 0))
);


--
-- Name: hrm_company_employee_id_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_company_employee_id_config (
    id integer NOT NULL,
    company_id uuid NOT NULL,
    last_sequence_number integer NOT NULL,
    id_prefix character varying(10) NOT NULL,
    created_by character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone
);


--
-- Name: hrm_company_employee_id_config_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_company_employee_id_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_company_employee_id_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_company_employee_id_config_id_seq OWNED BY public.hrm_company_employee_id_config.id;


--
-- Name: hrm_compliance_report; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_compliance_report (
    id integer NOT NULL,
    report_type character varying(20) NOT NULL,
    period_month integer NOT NULL,
    period_year integer NOT NULL,
    file_path character varying(255),
    file_name character varying(100),
    status character varying(20),
    total_employees integer,
    total_amount numeric(12,2),
    generated_by integer,
    generated_at timestamp without time zone,
    submitted_at timestamp without time zone
);


--
-- Name: hrm_compliance_report_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_compliance_report_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_compliance_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_compliance_report_id_seq OWNED BY public.hrm_compliance_report.id;


--
-- Name: hrm_departments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_departments (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    manager_id integer,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: hrm_departments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_departments_id_seq OWNED BY public.hrm_departments.id;


--
-- Name: hrm_designation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_designation (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying(100),
    modified_by character varying(100)
);


--
-- Name: hrm_designation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_designation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_designation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_designation_id_seq OWNED BY public.hrm_designation.id;


--
-- Name: hrm_designation_leave_allocation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_designation_leave_allocation (
    id integer NOT NULL,
    company_id uuid NOT NULL,
    designation_id integer NOT NULL,
    leave_type_id integer NOT NULL,
    total_days integer NOT NULL,
    created_by character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone
);


--
-- Name: hrm_designation_leave_allocation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_designation_leave_allocation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_designation_leave_allocation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_designation_leave_allocation_id_seq OWNED BY public.hrm_designation_leave_allocation.id;


--
-- Name: hrm_employee; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_employee (
    id integer NOT NULL,
    employee_id character varying(20) NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(120),
    phone character varying(20),
    nric character varying(20),
    date_of_birth date,
    gender character varying(10),
    nationality character varying(50),
    address text,
    postal_code character varying(10),
    profile_image_path character varying(255),
    department character varying(100),
    hire_date date NOT NULL,
    employment_type character varying(20),
    work_permit_type character varying(30),
    work_permit_expiry date,
    basic_salary numeric(10,2) NOT NULL,
    allowances numeric(10,2),
    hourly_rate numeric(8,2),
    cpf_account character varying(20),
    employee_cpf_rate numeric(5,2),
    employer_cpf_rate numeric(5,2),
    bank_name character varying(100),
    bank_account character varying(30),
    account_holder_name character varying(100),
    swift_code character varying(11),
    ifsc_code character varying(11),
    is_active boolean,
    termination_date date,
    user_id integer,
    organization_id integer,
    manager_id integer,
    working_hours_id integer,
    work_schedule_id integer,
    created_at timestamp without time zone,
    modified_at timestamp without time zone,
    company_id uuid,
    created_by character varying(100) DEFAULT 'system'::character varying,
    modified_by character varying(100),
    father_name character varying(100),
    work_permit_number character varying(50),
    timezone character varying(50) DEFAULT 'UTC'::character varying,
    location character varying(100),
    designation_id integer,
    overtime_group_id character varying(50),
    hazmat_expiry date,
    airport_pass_expiry date,
    psa_pass_number character varying(50),
    psa_pass_expiry date,
    is_manager boolean DEFAULT false,
    employee_group_id integer
);


--
-- Name: hrm_employee_bank_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_employee_bank_info (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    bank_account_name character varying(100),
    bank_account_number character varying(30),
    bank_code character varying(20),
    paynow_no character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: hrm_employee_bank_info_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_employee_bank_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_employee_bank_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_employee_bank_info_id_seq OWNED BY public.hrm_employee_bank_info.id;


--
-- Name: hrm_employee_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_employee_documents (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    document_type character varying(50) NOT NULL,
    file_path character varying(255) NOT NULL,
    issue_date date NOT NULL,
    month integer,
    year integer,
    description text,
    uploaded_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone
);


--
-- Name: hrm_employee_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_employee_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_employee_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_employee_documents_id_seq OWNED BY public.hrm_employee_documents.id;


--
-- Name: hrm_employee_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_employee_group (
    id integer NOT NULL,
    company_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    category character varying(50) NOT NULL,
    description text,
    is_active boolean NOT NULL,
    created_by character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone
);


--
-- Name: hrm_employee_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_employee_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_employee_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_employee_group_id_seq OWNED BY public.hrm_employee_group.id;


--
-- Name: hrm_employee_group_leave_allocation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_employee_group_leave_allocation (
    id integer NOT NULL,
    company_id uuid NOT NULL,
    employee_group_id integer NOT NULL,
    leave_type_id integer NOT NULL,
    total_days integer NOT NULL,
    created_by character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone
);


--
-- Name: hrm_employee_group_leave_allocation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_employee_group_leave_allocation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_employee_group_leave_allocation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_employee_group_leave_allocation_id_seq OWNED BY public.hrm_employee_group_leave_allocation.id;


--
-- Name: hrm_employee_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_employee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_employee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_employee_id_seq OWNED BY public.hrm_employee.id;


--
-- Name: hrm_employee_leave_allocation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_employee_leave_allocation (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    leave_type_id integer NOT NULL,
    total_days integer NOT NULL,
    override_reason text,
    created_by character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone
);


--
-- Name: hrm_employee_leave_allocation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_employee_leave_allocation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_employee_leave_allocation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_employee_leave_allocation_id_seq OWNED BY public.hrm_employee_leave_allocation.id;


--
-- Name: hrm_holiday; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_holiday (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    date date NOT NULL,
    type character varying(20) DEFAULT 'National'::character varying,
    company_id uuid,
    is_optional boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: hrm_holiday_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_holiday_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_holiday_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_holiday_id_seq OWNED BY public.hrm_holiday.id;


--
-- Name: hrm_job_execution_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_job_execution_log (
    id integer NOT NULL,
    job_name character varying(100) NOT NULL,
    status character varying(20),
    started_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    triggered_by character varying(50),
    details json
);


--
-- Name: hrm_job_execution_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_job_execution_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_job_execution_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_job_execution_log_id_seq OWNED BY public.hrm_job_execution_log.id;


--
-- Name: hrm_leave; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_leave (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    leave_type character varying(30) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    days_requested integer NOT NULL,
    reason text,
    status character varying(20),
    requested_by integer,
    approved_by integer,
    approved_at timestamp without time zone,
    rejection_reason text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: hrm_leave_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_leave_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_leave_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_leave_id_seq OWNED BY public.hrm_leave.id;


--
-- Name: hrm_leave_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_leave_type (
    id integer NOT NULL,
    company_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    description text,
    annual_allocation integer DEFAULT 0,
    color character varying(20) DEFAULT '#3498db'::character varying,
    is_active boolean DEFAULT true,
    created_by character varying(100) DEFAULT 'system'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone
);


--
-- Name: hrm_leave_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_leave_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_leave_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_leave_type_id_seq OWNED BY public.hrm_leave_type.id;


--
-- Name: hrm_ot_approval_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_ot_approval_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


--
-- Name: hrm_ot_approval; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_ot_approval (
    id integer DEFAULT nextval('public.hrm_ot_approval_id_seq'::regclass) NOT NULL,
    ot_request_id integer NOT NULL,
    approver_id integer NOT NULL,
    approval_level integer DEFAULT 1,
    status character varying(20) NOT NULL,
    comments text,
    approved_hours numeric(6,2),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: hrm_ot_attendance; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_ot_attendance (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    company_id uuid NOT NULL,
    ot_date date NOT NULL,
    ot_in_time timestamp without time zone,
    ot_out_time timestamp without time zone,
    ot_hours numeric(6,2),
    ot_type_id integer,
    status character varying(20) DEFAULT 'Draft'::character varying,
    notes text,
    latitude numeric(10,8),
    longitude numeric(11,8),
    created_by character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_at timestamp without time zone,
    quantity numeric(6,2) DEFAULT '0'::numeric,
    rate numeric(8,2) DEFAULT '0'::numeric,
    amount numeric(10,2) DEFAULT '0'::numeric
);


--
-- Name: hrm_ot_attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_ot_attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_ot_attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_ot_attendance_id_seq OWNED BY public.hrm_ot_attendance.id;


--
-- Name: hrm_ot_daily_summary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_ot_daily_summary (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    company_id uuid NOT NULL,
    ot_request_id integer,
    ot_date date NOT NULL,
    ot_hours numeric(6,2),
    ot_rate_per_hour numeric(8,2),
    ot_amount numeric(12,2),
    kd_and_claim numeric(12,2),
    trips numeric(12,2),
    sinpost numeric(12,2),
    sandstone numeric(12,2),
    spx numeric(12,2),
    psle numeric(12,2),
    manpower numeric(12,2),
    stacking numeric(12,2),
    dispose numeric(12,2),
    night numeric(12,2),
    ph numeric(12,2),
    sun numeric(12,2),
    total_allowances numeric(12,2),
    total_amount numeric(12,2),
    status character varying(20),
    notes text,
    created_by character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone,
    finalized_at timestamp without time zone,
    finalized_by character varying(100)
);


--
-- Name: hrm_ot_daily_summary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_ot_daily_summary_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_ot_daily_summary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_ot_daily_summary_id_seq OWNED BY public.hrm_ot_daily_summary.id;


--
-- Name: hrm_ot_request; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_ot_request (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    company_id uuid NOT NULL,
    ot_date date NOT NULL,
    ot_type_id integer NOT NULL,
    requested_hours numeric(6,2) NOT NULL,
    reason text NOT NULL,
    status character varying(20) DEFAULT 'Pending'::character varying,
    approved_hours numeric(6,2),
    approver_id integer,
    approval_comments text,
    approved_at timestamp without time zone,
    created_by character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_at timestamp without time zone,
    amount numeric(10,2) DEFAULT 0
);


--
-- Name: hrm_ot_request_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_ot_request_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_ot_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_ot_request_id_seq OWNED BY public.hrm_ot_request.id;


--
-- Name: hrm_ot_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_ot_type (
    id integer NOT NULL,
    company_id uuid,
    name character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    description text,
    rate_multiplier numeric(5,2) DEFAULT 1.5,
    color_code character varying(20) DEFAULT '#3498db'::character varying,
    is_active boolean DEFAULT true,
    display_order integer DEFAULT 0,
    created_by character varying(100) DEFAULT 'system'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone,
    monday boolean DEFAULT true,
    tuesday boolean DEFAULT true,
    wednesday boolean DEFAULT true,
    thursday boolean DEFAULT true,
    friday boolean DEFAULT true,
    saturday boolean DEFAULT false,
    sunday boolean DEFAULT false
);


--
-- Name: hrm_ot_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_ot_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_ot_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_ot_type_id_seq OWNED BY public.hrm_ot_type.id;


--
-- Name: hrm_payroll; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_payroll (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    pay_period_start date NOT NULL,
    pay_period_end date NOT NULL,
    basic_pay numeric(10,2) NOT NULL,
    overtime_pay numeric(10,2),
    allowances numeric(10,2),
    bonuses numeric(10,2),
    gross_pay numeric(10,2) NOT NULL,
    employee_cpf numeric(10,2),
    employer_cpf numeric(10,2),
    income_tax numeric(10,2),
    other_deductions numeric(10,2),
    net_pay numeric(10,2) NOT NULL,
    days_worked integer,
    overtime_hours numeric(5,2),
    leave_days integer,
    status character varying(20),
    generated_by integer,
    generated_at timestamp without time zone,
    absent_days integer DEFAULT 0,
    lop_days integer DEFAULT 0,
    lop_deduction numeric(10,2) DEFAULT 0
);


--
-- Name: hrm_payroll_configuration; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_payroll_configuration (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    allowance_1_name character varying(100),
    allowance_1_amount numeric(10,2),
    allowance_2_name character varying(100),
    allowance_2_amount numeric(10,2),
    allowance_3_name character varying(100),
    allowance_3_amount numeric(10,2),
    allowance_4_name character varying(100),
    allowance_4_amount numeric(10,2),
    ot_rate_per_hour numeric(8,2),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    updated_by integer,
    employer_cpf numeric,
    employee_cpf numeric,
    net_salary numeric,
    remarks text,
    levy_allowance_name character varying(100),
    levy_allowance_amount numeric(10,2) DEFAULT 0
);


--
-- Name: hrm_payroll_configuration_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_payroll_configuration_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_payroll_configuration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_payroll_configuration_id_seq OWNED BY public.hrm_payroll_configuration.id;


--
-- Name: hrm_payroll_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_payroll_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_payroll_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_payroll_id_seq OWNED BY public.hrm_payroll.id;


--
-- Name: hrm_payroll_ot_summary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_payroll_ot_summary (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    company_id uuid NOT NULL,
    payroll_month integer NOT NULL,
    payroll_year integer NOT NULL,
    total_ot_hours numeric(8,2) DEFAULT '0'::numeric,
    total_ot_amount numeric(12,2) DEFAULT '0'::numeric,
    general_ot_hours numeric(8,2) DEFAULT '0'::numeric,
    general_ot_amount numeric(12,2) DEFAULT '0'::numeric,
    weekend_ot_hours numeric(8,2) DEFAULT '0'::numeric,
    weekend_ot_amount numeric(12,2) DEFAULT '0'::numeric,
    holiday_ot_hours numeric(8,2) DEFAULT '0'::numeric,
    holiday_ot_amount numeric(12,2) DEFAULT '0'::numeric,
    sunday_ot_hours numeric(8,2) DEFAULT '0'::numeric,
    sunday_ot_amount numeric(12,2) DEFAULT '0'::numeric,
    status character varying(20) DEFAULT 'Draft'::character varying,
    daily_logs json,
    created_by character varying(100) DEFAULT 'system'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone,
    finalized_at timestamp without time zone
);


--
-- Name: hrm_payroll_ot_summary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_payroll_ot_summary_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_payroll_ot_summary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_payroll_ot_summary_id_seq OWNED BY public.hrm_payroll_ot_summary.id;


--
-- Name: hrm_role_access_control; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_role_access_control (
    id integer NOT NULL,
    module_name character varying(100) NOT NULL,
    menu_name character varying(100) NOT NULL,
    sub_menu_name character varying(100),
    super_admin_access character varying(20),
    tenant_admin_access character varying(20),
    hr_manager_access character varying(20),
    employee_access character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying(100),
    updated_by character varying(100)
);


--
-- Name: hrm_role_access_control_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_role_access_control_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_role_access_control_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_role_access_control_id_seq OWNED BY public.hrm_role_access_control.id;


--
-- Name: hrm_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_roles (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean DEFAULT true
);


--
-- Name: hrm_tenant; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_tenant (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_by character varying(100) DEFAULT 'system'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone,
    country_code character varying(10),
    currency_code character varying(10),
    CONSTRAINT chk_tenant_code_not_empty CHECK ((length(TRIM(BOTH FROM code)) > 0)),
    CONSTRAINT chk_tenant_name_not_empty CHECK ((length(TRIM(BOTH FROM name)) > 0))
);


--
-- Name: hrm_tenant_configuration; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_tenant_configuration (
    id integer NOT NULL,
    tenant_id uuid NOT NULL,
    payslip_logo_path character varying(255),
    payslip_logo_filename character varying(255),
    payslip_logo_uploaded_by character varying(100),
    payslip_logo_uploaded_at timestamp without time zone,
    employee_id_prefix character varying(50),
    employee_id_company_code character varying(20),
    employee_id_format character varying(100),
    employee_id_separator character varying(5),
    employee_id_next_number integer,
    employee_id_pad_length integer,
    employee_id_suffix character varying(50),
    overtime_enabled boolean,
    overtime_calculation_method character varying(20),
    overtime_group_type character varying(50),
    general_overtime_rate numeric(5,2),
    holiday_overtime_rate numeric(5,2),
    weekend_overtime_rate numeric(5,2),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    updated_by character varying(100)
);


--
-- Name: hrm_tenant_configuration_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_tenant_configuration_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_tenant_configuration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_tenant_configuration_id_seq OWNED BY public.hrm_tenant_configuration.id;


--
-- Name: hrm_tenant_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_tenant_documents (
    id integer NOT NULL,
    tenant_id uuid NOT NULL,
    file_name character varying(255) NOT NULL,
    file_path character varying(500) NOT NULL,
    file_type character varying(50),
    file_size integer,
    uploaded_by character varying(100) NOT NULL,
    upload_date timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: hrm_tenant_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_tenant_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_tenant_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_tenant_documents_id_seq OWNED BY public.hrm_tenant_documents.id;


--
-- Name: hrm_tenant_payment_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_tenant_payment_config (
    id integer NOT NULL,
    tenant_id uuid NOT NULL,
    payment_type character varying(20) DEFAULT 'Fixed'::character varying NOT NULL,
    implementation_charges numeric(10,2) DEFAULT 0,
    monthly_charges numeric(10,2) DEFAULT 0,
    other_charges numeric(10,2) DEFAULT 0,
    frequency character varying(20) DEFAULT 'Monthly'::character varying NOT NULL,
    created_by character varying(100) DEFAULT 'system'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_by character varying(100),
    modified_at timestamp without time zone,
    CONSTRAINT chk_frequency CHECK (((frequency)::text = ANY (ARRAY[('Monthly'::character varying)::text, ('Quarterly'::character varying)::text, ('Half-Yearly'::character varying)::text, ('Yearly'::character varying)::text]))),
    CONSTRAINT chk_payment_type CHECK (((payment_type)::text = ANY (ARRAY[('Fixed'::character varying)::text, ('User-Based'::character varying)::text])))
);


--
-- Name: hrm_tenant_payment_config_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_tenant_payment_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_tenant_payment_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_tenant_payment_config_id_seq OWNED BY public.hrm_tenant_payment_config.id;


--
-- Name: hrm_user_company_access; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_user_company_access (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id integer NOT NULL,
    company_id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_at timestamp without time zone
);


--
-- Name: hrm_user_role_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_user_role_mapping (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    company_id uuid,
    is_active boolean NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying(100)
);


--
-- Name: hrm_user_role_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_user_role_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_user_role_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_user_role_mapping_id_seq OWNED BY public.hrm_user_role_mapping.id;


--
-- Name: hrm_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_users (
    id integer NOT NULL,
    username character varying(120) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(256) NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    is_active boolean,
    must_reset_password boolean NOT NULL,
    organization_id integer NOT NULL,
    role_id integer NOT NULL,
    reporting_manager_id integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: hrm_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_users_id_seq OWNED BY public.hrm_users.id;


--
-- Name: hrm_work_schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_work_schedules (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    working_hours_id integer,
    monday boolean DEFAULT true,
    tuesday boolean DEFAULT true,
    wednesday boolean DEFAULT true,
    thursday boolean DEFAULT true,
    friday boolean DEFAULT true,
    saturday boolean DEFAULT false,
    sunday boolean DEFAULT false
);


--
-- Name: hrm_work_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_work_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_work_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_work_schedules_id_seq OWNED BY public.hrm_work_schedules.id;


--
-- Name: hrm_working_hours; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hrm_working_hours (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    hours_per_day numeric(4,2) NOT NULL,
    hours_per_week numeric(4,2) NOT NULL,
    description text,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    start_time time without time zone,
    end_time time without time zone,
    grace_period integer,
    late_mark_after_minutes integer DEFAULT 15,
    half_day_threshold integer DEFAULT 240,
    full_day_threshold integer DEFAULT 480,
    weekend_days character varying(20) DEFAULT '5,6'::character varying
);


--
-- Name: hrm_working_hours_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hrm_working_hours_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hrm_working_hours_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hrm_working_hours_id_seq OWNED BY public.hrm_working_hours.id;


--
-- Name: organization; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.organization (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp without time zone,
    modified_at timestamp without time zone,
    logo_path character varying(255),
    address text,
    uen character varying(50),
    tenant_id uuid,
    created_by character varying(100) DEFAULT 'system'::character varying,
    modified_by character varying(100)
);


--
-- Name: organization_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.organization_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.organization_id_seq OWNED BY public.organization.id;


--
-- Name: role_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.role_id_seq OWNED BY public.hrm_roles.id;


--
-- Name: hrm_appraisal id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_appraisal ALTER COLUMN id SET DEFAULT nextval('public.hrm_appraisal_id_seq'::regclass);


--
-- Name: hrm_attendance id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance ALTER COLUMN id SET DEFAULT nextval('public.hrm_attendance_id_seq'::regclass);


--
-- Name: hrm_attendance_regularization id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance_regularization ALTER COLUMN id SET DEFAULT nextval('public.hrm_attendance_regularization_id_seq'::regclass);


--
-- Name: hrm_attendance_segments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance_segments ALTER COLUMN id SET DEFAULT nextval('public.hrm_attendance_segments_id_seq'::regclass);


--
-- Name: hrm_audit_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_audit_log ALTER COLUMN id SET DEFAULT nextval('public.hrm_audit_log_id_seq'::regclass);


--
-- Name: hrm_claim id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_claim ALTER COLUMN id SET DEFAULT nextval('public.hrm_claim_id_seq'::regclass);


--
-- Name: hrm_company_employee_id_config id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_company_employee_id_config ALTER COLUMN id SET DEFAULT nextval('public.hrm_company_employee_id_config_id_seq'::regclass);


--
-- Name: hrm_compliance_report id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_compliance_report ALTER COLUMN id SET DEFAULT nextval('public.hrm_compliance_report_id_seq'::regclass);


--
-- Name: hrm_departments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_departments ALTER COLUMN id SET DEFAULT nextval('public.hrm_departments_id_seq'::regclass);


--
-- Name: hrm_designation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_designation ALTER COLUMN id SET DEFAULT nextval('public.hrm_designation_id_seq'::regclass);


--
-- Name: hrm_designation_leave_allocation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_designation_leave_allocation ALTER COLUMN id SET DEFAULT nextval('public.hrm_designation_leave_allocation_id_seq'::regclass);


--
-- Name: hrm_employee id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee ALTER COLUMN id SET DEFAULT nextval('public.hrm_employee_id_seq'::regclass);


--
-- Name: hrm_employee_bank_info id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_bank_info ALTER COLUMN id SET DEFAULT nextval('public.hrm_employee_bank_info_id_seq'::regclass);


--
-- Name: hrm_employee_documents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_documents ALTER COLUMN id SET DEFAULT nextval('public.hrm_employee_documents_id_seq'::regclass);


--
-- Name: hrm_employee_group id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group ALTER COLUMN id SET DEFAULT nextval('public.hrm_employee_group_id_seq'::regclass);


--
-- Name: hrm_employee_group_leave_allocation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group_leave_allocation ALTER COLUMN id SET DEFAULT nextval('public.hrm_employee_group_leave_allocation_id_seq'::regclass);


--
-- Name: hrm_employee_leave_allocation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_leave_allocation ALTER COLUMN id SET DEFAULT nextval('public.hrm_employee_leave_allocation_id_seq'::regclass);


--
-- Name: hrm_holiday id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_holiday ALTER COLUMN id SET DEFAULT nextval('public.hrm_holiday_id_seq'::regclass);


--
-- Name: hrm_job_execution_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_job_execution_log ALTER COLUMN id SET DEFAULT nextval('public.hrm_job_execution_log_id_seq'::regclass);


--
-- Name: hrm_leave id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_leave ALTER COLUMN id SET DEFAULT nextval('public.hrm_leave_id_seq'::regclass);


--
-- Name: hrm_leave_type id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_leave_type ALTER COLUMN id SET DEFAULT nextval('public.hrm_leave_type_id_seq'::regclass);


--
-- Name: hrm_ot_attendance id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_attendance ALTER COLUMN id SET DEFAULT nextval('public.hrm_ot_attendance_id_seq'::regclass);


--
-- Name: hrm_ot_daily_summary id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_daily_summary ALTER COLUMN id SET DEFAULT nextval('public.hrm_ot_daily_summary_id_seq'::regclass);


--
-- Name: hrm_ot_request id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_request ALTER COLUMN id SET DEFAULT nextval('public.hrm_ot_request_id_seq'::regclass);


--
-- Name: hrm_ot_type id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_type ALTER COLUMN id SET DEFAULT nextval('public.hrm_ot_type_id_seq'::regclass);


--
-- Name: hrm_payroll id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll ALTER COLUMN id SET DEFAULT nextval('public.hrm_payroll_id_seq'::regclass);


--
-- Name: hrm_payroll_configuration id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_configuration ALTER COLUMN id SET DEFAULT nextval('public.hrm_payroll_configuration_id_seq'::regclass);


--
-- Name: hrm_payroll_ot_summary id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_ot_summary ALTER COLUMN id SET DEFAULT nextval('public.hrm_payroll_ot_summary_id_seq'::regclass);


--
-- Name: hrm_role_access_control id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_role_access_control ALTER COLUMN id SET DEFAULT nextval('public.hrm_role_access_control_id_seq'::regclass);


--
-- Name: hrm_roles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_roles ALTER COLUMN id SET DEFAULT nextval('public.role_id_seq'::regclass);


--
-- Name: hrm_tenant_configuration id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_configuration ALTER COLUMN id SET DEFAULT nextval('public.hrm_tenant_configuration_id_seq'::regclass);


--
-- Name: hrm_tenant_documents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_documents ALTER COLUMN id SET DEFAULT nextval('public.hrm_tenant_documents_id_seq'::regclass);


--
-- Name: hrm_tenant_payment_config id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_payment_config ALTER COLUMN id SET DEFAULT nextval('public.hrm_tenant_payment_config_id_seq'::regclass);


--
-- Name: hrm_user_role_mapping id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_user_role_mapping ALTER COLUMN id SET DEFAULT nextval('public.hrm_user_role_mapping_id_seq'::regclass);


--
-- Name: hrm_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_users ALTER COLUMN id SET DEFAULT nextval('public.hrm_users_id_seq'::regclass);


--
-- Name: hrm_work_schedules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_work_schedules ALTER COLUMN id SET DEFAULT nextval('public.hrm_work_schedules_id_seq'::regclass);


--
-- Name: hrm_working_hours id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_working_hours ALTER COLUMN id SET DEFAULT nextval('public.hrm_working_hours_id_seq'::regclass);


--
-- Name: organization id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organization ALTER COLUMN id SET DEFAULT nextval('public.organization_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: hrm_appraisal hrm_appraisal_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_appraisal
    ADD CONSTRAINT hrm_appraisal_pkey PRIMARY KEY (id);


--
-- Name: hrm_attendance hrm_attendance_employee_id_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance
    ADD CONSTRAINT hrm_attendance_employee_id_date_key UNIQUE (employee_id, date);


--
-- Name: hrm_attendance hrm_attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance
    ADD CONSTRAINT hrm_attendance_pkey PRIMARY KEY (id);


--
-- Name: hrm_attendance_regularization hrm_attendance_regularization_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance_regularization
    ADD CONSTRAINT hrm_attendance_regularization_pkey PRIMARY KEY (id);


--
-- Name: hrm_attendance_segments hrm_attendance_segments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance_segments
    ADD CONSTRAINT hrm_attendance_segments_pkey PRIMARY KEY (id);


--
-- Name: hrm_audit_log hrm_audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_audit_log
    ADD CONSTRAINT hrm_audit_log_pkey PRIMARY KEY (id);


--
-- Name: hrm_claim hrm_claim_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_claim
    ADD CONSTRAINT hrm_claim_pkey PRIMARY KEY (id);


--
-- Name: hrm_company_employee_id_config hrm_company_employee_id_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_company_employee_id_config
    ADD CONSTRAINT hrm_company_employee_id_config_pkey PRIMARY KEY (id);


--
-- Name: hrm_company hrm_company_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_company
    ADD CONSTRAINT hrm_company_pkey PRIMARY KEY (id);


--
-- Name: hrm_compliance_report hrm_compliance_report_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_compliance_report
    ADD CONSTRAINT hrm_compliance_report_pkey PRIMARY KEY (id);


--
-- Name: hrm_departments hrm_departments_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_departments
    ADD CONSTRAINT hrm_departments_name_key UNIQUE (name);


--
-- Name: hrm_departments hrm_departments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_departments
    ADD CONSTRAINT hrm_departments_pkey PRIMARY KEY (id);


--
-- Name: hrm_designation_leave_allocation hrm_designation_leave_allocation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_designation_leave_allocation
    ADD CONSTRAINT hrm_designation_leave_allocation_pkey PRIMARY KEY (id);


--
-- Name: hrm_designation hrm_designation_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_designation
    ADD CONSTRAINT hrm_designation_name_key UNIQUE (name);


--
-- Name: hrm_designation hrm_designation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_designation
    ADD CONSTRAINT hrm_designation_pkey PRIMARY KEY (id);


--
-- Name: hrm_employee_bank_info hrm_employee_bank_info_employee_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_bank_info
    ADD CONSTRAINT hrm_employee_bank_info_employee_id_key UNIQUE (employee_id);


--
-- Name: hrm_employee_bank_info hrm_employee_bank_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_bank_info
    ADD CONSTRAINT hrm_employee_bank_info_pkey PRIMARY KEY (id);


--
-- Name: hrm_employee_documents hrm_employee_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_documents
    ADD CONSTRAINT hrm_employee_documents_pkey PRIMARY KEY (id);


--
-- Name: hrm_employee hrm_employee_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_email_key UNIQUE (email);


--
-- Name: hrm_employee hrm_employee_employee_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_employee_id_key UNIQUE (employee_id);


--
-- Name: hrm_employee_group_leave_allocation hrm_employee_group_leave_allocation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group_leave_allocation
    ADD CONSTRAINT hrm_employee_group_leave_allocation_pkey PRIMARY KEY (id);


--
-- Name: hrm_employee_group hrm_employee_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group
    ADD CONSTRAINT hrm_employee_group_pkey PRIMARY KEY (id);


--
-- Name: hrm_employee_leave_allocation hrm_employee_leave_allocation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_leave_allocation
    ADD CONSTRAINT hrm_employee_leave_allocation_pkey PRIMARY KEY (id);


--
-- Name: hrm_employee hrm_employee_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_pkey PRIMARY KEY (id);


--
-- Name: hrm_holiday hrm_holiday_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_holiday
    ADD CONSTRAINT hrm_holiday_pkey PRIMARY KEY (id);


--
-- Name: hrm_job_execution_log hrm_job_execution_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_job_execution_log
    ADD CONSTRAINT hrm_job_execution_log_pkey PRIMARY KEY (id);


--
-- Name: hrm_leave hrm_leave_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_leave
    ADD CONSTRAINT hrm_leave_pkey PRIMARY KEY (id);


--
-- Name: hrm_leave_type hrm_leave_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_leave_type
    ADD CONSTRAINT hrm_leave_type_pkey PRIMARY KEY (id);


--
-- Name: hrm_ot_approval hrm_ot_approval_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_approval
    ADD CONSTRAINT hrm_ot_approval_pkey PRIMARY KEY (id);


--
-- Name: hrm_ot_attendance hrm_ot_attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_attendance
    ADD CONSTRAINT hrm_ot_attendance_pkey PRIMARY KEY (id);


--
-- Name: hrm_ot_daily_summary hrm_ot_daily_summary_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_daily_summary
    ADD CONSTRAINT hrm_ot_daily_summary_pkey PRIMARY KEY (id);


--
-- Name: hrm_ot_request hrm_ot_request_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_request
    ADD CONSTRAINT hrm_ot_request_pkey PRIMARY KEY (id);


--
-- Name: hrm_ot_type hrm_ot_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_type
    ADD CONSTRAINT hrm_ot_type_pkey PRIMARY KEY (id);


--
-- Name: hrm_payroll_configuration hrm_payroll_configuration_employee_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_configuration
    ADD CONSTRAINT hrm_payroll_configuration_employee_id_key UNIQUE (employee_id);


--
-- Name: hrm_payroll_configuration hrm_payroll_configuration_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_configuration
    ADD CONSTRAINT hrm_payroll_configuration_pkey PRIMARY KEY (id);


--
-- Name: hrm_payroll_ot_summary hrm_payroll_ot_summary_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_ot_summary
    ADD CONSTRAINT hrm_payroll_ot_summary_pkey PRIMARY KEY (id);


--
-- Name: hrm_payroll hrm_payroll_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll
    ADD CONSTRAINT hrm_payroll_pkey PRIMARY KEY (id);


--
-- Name: hrm_role_access_control hrm_role_access_control_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_role_access_control
    ADD CONSTRAINT hrm_role_access_control_pkey PRIMARY KEY (id);


--
-- Name: hrm_tenant hrm_tenant_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant
    ADD CONSTRAINT hrm_tenant_code_key UNIQUE (code);


--
-- Name: hrm_tenant_configuration hrm_tenant_configuration_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_configuration
    ADD CONSTRAINT hrm_tenant_configuration_pkey PRIMARY KEY (id);


--
-- Name: hrm_tenant_documents hrm_tenant_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_documents
    ADD CONSTRAINT hrm_tenant_documents_pkey PRIMARY KEY (id);


--
-- Name: hrm_tenant hrm_tenant_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant
    ADD CONSTRAINT hrm_tenant_name_key UNIQUE (name);


--
-- Name: hrm_tenant_payment_config hrm_tenant_payment_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_payment_config
    ADD CONSTRAINT hrm_tenant_payment_config_pkey PRIMARY KEY (id);


--
-- Name: hrm_tenant hrm_tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant
    ADD CONSTRAINT hrm_tenant_pkey PRIMARY KEY (id);


--
-- Name: hrm_user_company_access hrm_user_company_access_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_user_company_access
    ADD CONSTRAINT hrm_user_company_access_pkey PRIMARY KEY (id);


--
-- Name: hrm_user_role_mapping hrm_user_role_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_user_role_mapping
    ADD CONSTRAINT hrm_user_role_mapping_pkey PRIMARY KEY (id);


--
-- Name: hrm_users hrm_users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_users
    ADD CONSTRAINT hrm_users_email_key UNIQUE (email);


--
-- Name: hrm_users hrm_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_users
    ADD CONSTRAINT hrm_users_pkey PRIMARY KEY (id);


--
-- Name: hrm_users hrm_users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_users
    ADD CONSTRAINT hrm_users_username_key UNIQUE (username);


--
-- Name: hrm_work_schedules hrm_work_schedules_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_work_schedules
    ADD CONSTRAINT hrm_work_schedules_name_key UNIQUE (name);


--
-- Name: hrm_work_schedules hrm_work_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_work_schedules
    ADD CONSTRAINT hrm_work_schedules_pkey PRIMARY KEY (id);


--
-- Name: hrm_working_hours hrm_working_hours_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_working_hours
    ADD CONSTRAINT hrm_working_hours_name_key UNIQUE (name);


--
-- Name: hrm_working_hours hrm_working_hours_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_working_hours
    ADD CONSTRAINT hrm_working_hours_pkey PRIMARY KEY (id);


--
-- Name: organization organization_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organization
    ADD CONSTRAINT organization_name_key UNIQUE (name);


--
-- Name: organization organization_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organization
    ADD CONSTRAINT organization_pkey PRIMARY KEY (id);


--
-- Name: hrm_roles role_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_roles
    ADD CONSTRAINT role_name_key UNIQUE (name);


--
-- Name: hrm_roles role_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_roles
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: hrm_company_employee_id_config uq_company_id_config; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_company_employee_id_config
    ADD CONSTRAINT uq_company_id_config UNIQUE (company_id);


--
-- Name: hrm_company uq_company_tenant_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_company
    ADD CONSTRAINT uq_company_tenant_code UNIQUE (tenant_id, code);


--
-- Name: hrm_designation_leave_allocation uq_designation_leave_type; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_designation_leave_allocation
    ADD CONSTRAINT uq_designation_leave_type UNIQUE (company_id, designation_id, leave_type_id);


--
-- Name: hrm_employee_group uq_employee_group_company_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group
    ADD CONSTRAINT uq_employee_group_company_name UNIQUE (company_id, name);


--
-- Name: hrm_employee_group_leave_allocation uq_employee_group_leave_type; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group_leave_allocation
    ADD CONSTRAINT uq_employee_group_leave_type UNIQUE (company_id, employee_group_id, leave_type_id);


--
-- Name: hrm_employee_leave_allocation uq_employee_leave_type; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_leave_allocation
    ADD CONSTRAINT uq_employee_leave_type UNIQUE (employee_id, leave_type_id);


--
-- Name: hrm_leave_type uq_leave_type_company_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_leave_type
    ADD CONSTRAINT uq_leave_type_company_name UNIQUE (company_id, name);


--
-- Name: hrm_ot_daily_summary uq_ot_daily_emp_date; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_daily_summary
    ADD CONSTRAINT uq_ot_daily_emp_date UNIQUE (employee_id, ot_date);


--
-- Name: hrm_ot_type uq_ot_type_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_type
    ADD CONSTRAINT uq_ot_type_code UNIQUE (code);


--
-- Name: hrm_payroll_ot_summary uq_payroll_ot_emp_month_year; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_ot_summary
    ADD CONSTRAINT uq_payroll_ot_emp_month_year UNIQUE (employee_id, payroll_month, payroll_year);


--
-- Name: hrm_tenant_configuration uq_tenant_config_tenant; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_configuration
    ADD CONSTRAINT uq_tenant_config_tenant UNIQUE (tenant_id);


--
-- Name: hrm_user_company_access uq_user_company_access; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_user_company_access
    ADD CONSTRAINT uq_user_company_access UNIQUE (user_id, company_id);


--
-- Name: idx_audit_log_action; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_log_action ON public.hrm_audit_log USING btree (action);


--
-- Name: idx_audit_log_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_log_created_at ON public.hrm_audit_log USING btree (created_at);


--
-- Name: idx_audit_log_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_log_user_id ON public.hrm_audit_log USING btree (user_id);


--
-- Name: idx_company_employee_id_config_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_company_employee_id_config_company_id ON public.hrm_company_employee_id_config USING btree (company_id);


--
-- Name: idx_designation_leave_alloc_company; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_designation_leave_alloc_company ON public.hrm_designation_leave_allocation USING btree (company_id);


--
-- Name: idx_designation_leave_alloc_designation; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_designation_leave_alloc_designation ON public.hrm_designation_leave_allocation USING btree (designation_id);


--
-- Name: idx_designation_leave_alloc_leave_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_designation_leave_alloc_leave_type ON public.hrm_designation_leave_allocation USING btree (leave_type_id);


--
-- Name: idx_emp_group_leave_alloc_company; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_emp_group_leave_alloc_company ON public.hrm_employee_group_leave_allocation USING btree (company_id);


--
-- Name: idx_emp_group_leave_alloc_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_emp_group_leave_alloc_group ON public.hrm_employee_group_leave_allocation USING btree (employee_group_id);


--
-- Name: idx_emp_group_leave_alloc_leave_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_emp_group_leave_alloc_leave_type ON public.hrm_employee_group_leave_allocation USING btree (leave_type_id);


--
-- Name: idx_emp_leave_alloc_employee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_emp_leave_alloc_employee ON public.hrm_employee_leave_allocation USING btree (employee_id);


--
-- Name: idx_emp_leave_alloc_leave_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_emp_leave_alloc_leave_type ON public.hrm_employee_leave_allocation USING btree (leave_type_id);


--
-- Name: idx_hrm_company_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_company_code ON public.hrm_company USING btree (code);


--
-- Name: idx_hrm_company_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_company_created_at ON public.hrm_company USING btree (created_at);


--
-- Name: idx_hrm_company_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_company_is_active ON public.hrm_company USING btree (is_active);


--
-- Name: idx_hrm_company_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_company_tenant_id ON public.hrm_company USING btree (tenant_id);


--
-- Name: idx_hrm_employee_group_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_employee_group_company_id ON public.hrm_employee_group USING btree (company_id);


--
-- Name: idx_hrm_employee_group_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_employee_group_is_active ON public.hrm_employee_group USING btree (is_active);


--
-- Name: idx_hrm_leave_type_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_leave_type_company_id ON public.hrm_leave_type USING btree (company_id);


--
-- Name: idx_hrm_leave_type_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_leave_type_is_active ON public.hrm_leave_type USING btree (is_active);


--
-- Name: idx_hrm_tenant_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_tenant_code ON public.hrm_tenant USING btree (code);


--
-- Name: idx_hrm_tenant_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_tenant_created_at ON public.hrm_tenant USING btree (created_at);


--
-- Name: idx_hrm_tenant_documents_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_tenant_documents_tenant_id ON public.hrm_tenant_documents USING btree (tenant_id);


--
-- Name: idx_hrm_tenant_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_tenant_is_active ON public.hrm_tenant USING btree (is_active);


--
-- Name: idx_hrm_tenant_payment_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hrm_tenant_payment_tenant_id ON public.hrm_tenant_payment_config USING btree (tenant_id);


--
-- Name: idx_job_log_job_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_job_log_job_name ON public.hrm_job_execution_log USING btree (job_name);


--
-- Name: idx_job_log_started_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_job_log_started_at ON public.hrm_job_execution_log USING btree (started_at);


--
-- Name: idx_job_log_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_job_log_status ON public.hrm_job_execution_log USING btree (status);


--
-- Name: idx_ot_attendance_employee_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ot_attendance_employee_date ON public.hrm_ot_attendance USING btree (employee_id, ot_date);


--
-- Name: idx_ot_daily_employee_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ot_daily_employee_date ON public.hrm_ot_daily_summary USING btree (employee_id, ot_date);


--
-- Name: idx_ot_request_employee_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ot_request_employee_id ON public.hrm_ot_request USING btree (employee_id);


--
-- Name: idx_ot_request_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ot_request_status ON public.hrm_ot_request USING btree (status);


--
-- Name: idx_ot_type_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ot_type_company_id ON public.hrm_ot_type USING btree (company_id);


--
-- Name: idx_role_access_module_menu; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_role_access_module_menu ON public.hrm_role_access_control USING btree (module_name, menu_name);


--
-- Name: idx_tenant_config_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_config_tenant_id ON public.hrm_tenant_configuration USING btree (tenant_id);


--
-- Name: idx_user_role_mapping_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_role_mapping_user_id ON public.hrm_user_role_mapping USING btree (user_id);


--
-- Name: ix_hrm_employee_bank_info_employee_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hrm_employee_bank_info_employee_id ON public.hrm_employee_bank_info USING btree (employee_id);


--
-- Name: ix_hrm_employee_documents_document_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hrm_employee_documents_document_type ON public.hrm_employee_documents USING btree (document_type);


--
-- Name: ix_hrm_employee_documents_employee_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hrm_employee_documents_employee_id ON public.hrm_employee_documents USING btree (employee_id);


--
-- Name: ix_hrm_employee_documents_year_month; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hrm_employee_documents_year_month ON public.hrm_employee_documents USING btree (year, month);


--
-- Name: ix_hrm_payroll_config_employee_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hrm_payroll_config_employee_id ON public.hrm_payroll_configuration USING btree (employee_id);


--
-- Name: ix_hrm_users_organization_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hrm_users_organization_id ON public.hrm_users USING btree (organization_id);


--
-- Name: ix_hrm_users_reporting_manager_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hrm_users_reporting_manager_id ON public.hrm_users USING btree (reporting_manager_id);


--
-- Name: ix_hrm_users_role_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hrm_users_role_id ON public.hrm_users USING btree (role_id);


--
-- Name: ix_user_company_access_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_company_access_company_id ON public.hrm_user_company_access USING btree (company_id);


--
-- Name: ix_user_company_access_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_company_access_user_id ON public.hrm_user_company_access USING btree (user_id);


--
-- Name: hrm_company trg_hrm_company_modified_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_hrm_company_modified_at BEFORE UPDATE ON public.hrm_company FOR EACH ROW EXECUTE FUNCTION public.update_modified_at_column();


--
-- Name: hrm_employee trg_hrm_employee_modified_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_hrm_employee_modified_at BEFORE UPDATE ON public.hrm_employee FOR EACH ROW EXECUTE FUNCTION public.update_modified_at_column();


--
-- Name: hrm_tenant trg_hrm_tenant_modified_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_hrm_tenant_modified_at BEFORE UPDATE ON public.hrm_tenant FOR EACH ROW EXECUTE FUNCTION public.update_modified_at_column();


--
-- Name: hrm_tenant_payment_config trg_hrm_tenant_payment_config_modified_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_hrm_tenant_payment_config_modified_at BEFORE UPDATE ON public.hrm_tenant_payment_config FOR EACH ROW EXECUTE FUNCTION public.update_modified_at_column();


--
-- Name: organization trg_organization_modified_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_organization_modified_at BEFORE UPDATE ON public.organization FOR EACH ROW EXECUTE FUNCTION public.update_modified_at_column();


--
-- Name: hrm_attendance fk_attendance_overtime_approver; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance
    ADD CONSTRAINT fk_attendance_overtime_approver FOREIGN KEY (overtime_approved_by) REFERENCES public.hrm_users(id) ON DELETE SET NULL;


--
-- Name: hrm_company fk_company_tenant; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_company
    ADD CONSTRAINT fk_company_tenant FOREIGN KEY (tenant_id) REFERENCES public.hrm_tenant(id) ON DELETE CASCADE;


--
-- Name: hrm_employee fk_employee_company; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT fk_employee_company FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: organization fk_organization_tenant; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organization
    ADD CONSTRAINT fk_organization_tenant FOREIGN KEY (tenant_id) REFERENCES public.hrm_tenant(id) ON DELETE SET NULL;


--
-- Name: hrm_tenant_payment_config fk_payment_config_tenant; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_payment_config
    ADD CONSTRAINT fk_payment_config_tenant FOREIGN KEY (tenant_id) REFERENCES public.hrm_tenant(id) ON DELETE CASCADE;


--
-- Name: hrm_tenant_documents fk_tenant_documents_tenant; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_documents
    ADD CONSTRAINT fk_tenant_documents_tenant FOREIGN KEY (tenant_id) REFERENCES public.hrm_tenant(id) ON DELETE CASCADE;


--
-- Name: hrm_user_company_access fk_user_company_access_company; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_user_company_access
    ADD CONSTRAINT fk_user_company_access_company FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_user_company_access fk_user_company_access_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_user_company_access
    ADD CONSTRAINT fk_user_company_access_user FOREIGN KEY (user_id) REFERENCES public.hrm_users(id) ON DELETE CASCADE;


--
-- Name: hrm_appraisal hrm_appraisal_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_appraisal
    ADD CONSTRAINT hrm_appraisal_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id);


--
-- Name: hrm_appraisal hrm_appraisal_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_appraisal
    ADD CONSTRAINT hrm_appraisal_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_attendance hrm_attendance_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance
    ADD CONSTRAINT hrm_attendance_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id);


--
-- Name: hrm_attendance hrm_attendance_leave_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance
    ADD CONSTRAINT hrm_attendance_leave_id_fkey FOREIGN KEY (leave_id) REFERENCES public.hrm_leave(id);


--
-- Name: hrm_attendance_regularization hrm_attendance_regularization_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance_regularization
    ADD CONSTRAINT hrm_attendance_regularization_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_attendance_regularization hrm_attendance_regularization_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance_regularization
    ADD CONSTRAINT hrm_attendance_regularization_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id);


--
-- Name: hrm_attendance hrm_attendance_regularization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance
    ADD CONSTRAINT hrm_attendance_regularization_id_fkey FOREIGN KEY (regularization_id) REFERENCES public.hrm_attendance_regularization(id);


--
-- Name: hrm_attendance_regularization hrm_attendance_regularization_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance_regularization
    ADD CONSTRAINT hrm_attendance_regularization_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_attendance_segments hrm_attendance_segments_attendance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_attendance_segments
    ADD CONSTRAINT hrm_attendance_segments_attendance_id_fkey FOREIGN KEY (attendance_id) REFERENCES public.hrm_attendance(id) ON DELETE CASCADE;


--
-- Name: hrm_audit_log hrm_audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_audit_log
    ADD CONSTRAINT hrm_audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.hrm_users(id) ON DELETE SET NULL;


--
-- Name: hrm_claim hrm_claim_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_claim
    ADD CONSTRAINT hrm_claim_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_claim hrm_claim_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_claim
    ADD CONSTRAINT hrm_claim_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id);


--
-- Name: hrm_claim hrm_claim_submitted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_claim
    ADD CONSTRAINT hrm_claim_submitted_by_fkey FOREIGN KEY (submitted_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_company_employee_id_config hrm_company_employee_id_config_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_company_employee_id_config
    ADD CONSTRAINT hrm_company_employee_id_config_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_compliance_report hrm_compliance_report_generated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_compliance_report
    ADD CONSTRAINT hrm_compliance_report_generated_by_fkey FOREIGN KEY (generated_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_departments hrm_departments_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_departments
    ADD CONSTRAINT hrm_departments_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.hrm_employee(id);


--
-- Name: hrm_designation_leave_allocation hrm_designation_leave_allocation_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_designation_leave_allocation
    ADD CONSTRAINT hrm_designation_leave_allocation_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_designation_leave_allocation hrm_designation_leave_allocation_designation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_designation_leave_allocation
    ADD CONSTRAINT hrm_designation_leave_allocation_designation_id_fkey FOREIGN KEY (designation_id) REFERENCES public.hrm_designation(id) ON DELETE CASCADE;


--
-- Name: hrm_designation_leave_allocation hrm_designation_leave_allocation_leave_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_designation_leave_allocation
    ADD CONSTRAINT hrm_designation_leave_allocation_leave_type_id_fkey FOREIGN KEY (leave_type_id) REFERENCES public.hrm_leave_type(id) ON DELETE CASCADE;


--
-- Name: hrm_employee_bank_info hrm_employee_bank_info_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_bank_info
    ADD CONSTRAINT hrm_employee_bank_info_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id) ON DELETE CASCADE;


--
-- Name: hrm_employee hrm_employee_designation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_designation_id_fkey FOREIGN KEY (designation_id) REFERENCES public.hrm_designation(id);


--
-- Name: hrm_employee_documents hrm_employee_documents_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_documents
    ADD CONSTRAINT hrm_employee_documents_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id) ON DELETE CASCADE;


--
-- Name: hrm_employee_documents hrm_employee_documents_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_documents
    ADD CONSTRAINT hrm_employee_documents_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.hrm_users(id) ON DELETE SET NULL;


--
-- Name: hrm_employee hrm_employee_employee_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_employee_group_id_fkey FOREIGN KEY (employee_group_id) REFERENCES public.hrm_employee_group(id);


--
-- Name: hrm_employee_group hrm_employee_group_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group
    ADD CONSTRAINT hrm_employee_group_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_employee_group_leave_allocation hrm_employee_group_leave_allocation_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group_leave_allocation
    ADD CONSTRAINT hrm_employee_group_leave_allocation_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_employee_group_leave_allocation hrm_employee_group_leave_allocation_employee_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group_leave_allocation
    ADD CONSTRAINT hrm_employee_group_leave_allocation_employee_group_id_fkey FOREIGN KEY (employee_group_id) REFERENCES public.hrm_employee_group(id) ON DELETE CASCADE;


--
-- Name: hrm_employee_group_leave_allocation hrm_employee_group_leave_allocation_leave_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_group_leave_allocation
    ADD CONSTRAINT hrm_employee_group_leave_allocation_leave_type_id_fkey FOREIGN KEY (leave_type_id) REFERENCES public.hrm_leave_type(id) ON DELETE CASCADE;


--
-- Name: hrm_employee_leave_allocation hrm_employee_leave_allocation_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_leave_allocation
    ADD CONSTRAINT hrm_employee_leave_allocation_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id) ON DELETE CASCADE;


--
-- Name: hrm_employee_leave_allocation hrm_employee_leave_allocation_leave_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee_leave_allocation
    ADD CONSTRAINT hrm_employee_leave_allocation_leave_type_id_fkey FOREIGN KEY (leave_type_id) REFERENCES public.hrm_leave_type(id) ON DELETE CASCADE;


--
-- Name: hrm_employee hrm_employee_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.hrm_employee(id) ON DELETE SET NULL;


--
-- Name: hrm_employee hrm_employee_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organization(id);


--
-- Name: hrm_employee hrm_employee_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.hrm_users(id);


--
-- Name: hrm_employee hrm_employee_work_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_work_schedule_id_fkey FOREIGN KEY (work_schedule_id) REFERENCES public.hrm_work_schedules(id);


--
-- Name: hrm_employee hrm_employee_working_hours_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_employee
    ADD CONSTRAINT hrm_employee_working_hours_id_fkey FOREIGN KEY (working_hours_id) REFERENCES public.hrm_working_hours(id);


--
-- Name: hrm_holiday hrm_holiday_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_holiday
    ADD CONSTRAINT hrm_holiday_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id);


--
-- Name: hrm_leave hrm_leave_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_leave
    ADD CONSTRAINT hrm_leave_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_leave hrm_leave_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_leave
    ADD CONSTRAINT hrm_leave_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id);


--
-- Name: hrm_leave hrm_leave_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_leave
    ADD CONSTRAINT hrm_leave_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_leave_type hrm_leave_type_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_leave_type
    ADD CONSTRAINT hrm_leave_type_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_ot_approval hrm_ot_approval_approver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_approval
    ADD CONSTRAINT hrm_ot_approval_approver_id_fkey FOREIGN KEY (approver_id) REFERENCES public.hrm_users(id);


--
-- Name: hrm_ot_approval hrm_ot_approval_ot_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_approval
    ADD CONSTRAINT hrm_ot_approval_ot_request_id_fkey FOREIGN KEY (ot_request_id) REFERENCES public.hrm_ot_request(id) ON DELETE CASCADE;


--
-- Name: hrm_ot_attendance hrm_ot_attendance_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_attendance
    ADD CONSTRAINT hrm_ot_attendance_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_ot_attendance hrm_ot_attendance_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_attendance
    ADD CONSTRAINT hrm_ot_attendance_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id) ON DELETE CASCADE;


--
-- Name: hrm_ot_attendance hrm_ot_attendance_ot_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_attendance
    ADD CONSTRAINT hrm_ot_attendance_ot_type_id_fkey FOREIGN KEY (ot_type_id) REFERENCES public.hrm_ot_type(id);


--
-- Name: hrm_ot_daily_summary hrm_ot_daily_summary_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_daily_summary
    ADD CONSTRAINT hrm_ot_daily_summary_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_ot_daily_summary hrm_ot_daily_summary_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_daily_summary
    ADD CONSTRAINT hrm_ot_daily_summary_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id) ON DELETE CASCADE;


--
-- Name: hrm_ot_daily_summary hrm_ot_daily_summary_ot_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_daily_summary
    ADD CONSTRAINT hrm_ot_daily_summary_ot_request_id_fkey FOREIGN KEY (ot_request_id) REFERENCES public.hrm_ot_request(id) ON DELETE SET NULL;


--
-- Name: hrm_ot_request hrm_ot_request_approver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_request
    ADD CONSTRAINT hrm_ot_request_approver_id_fkey FOREIGN KEY (approver_id) REFERENCES public.hrm_users(id);


--
-- Name: hrm_ot_request hrm_ot_request_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_request
    ADD CONSTRAINT hrm_ot_request_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_ot_request hrm_ot_request_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_request
    ADD CONSTRAINT hrm_ot_request_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id) ON DELETE CASCADE;


--
-- Name: hrm_ot_request hrm_ot_request_ot_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_request
    ADD CONSTRAINT hrm_ot_request_ot_type_id_fkey FOREIGN KEY (ot_type_id) REFERENCES public.hrm_ot_type(id);


--
-- Name: hrm_ot_type hrm_ot_type_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_ot_type
    ADD CONSTRAINT hrm_ot_type_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_payroll_configuration hrm_payroll_configuration_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_configuration
    ADD CONSTRAINT hrm_payroll_configuration_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id);


--
-- Name: hrm_payroll_configuration hrm_payroll_configuration_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_configuration
    ADD CONSTRAINT hrm_payroll_configuration_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_payroll hrm_payroll_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll
    ADD CONSTRAINT hrm_payroll_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id);


--
-- Name: hrm_payroll hrm_payroll_generated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll
    ADD CONSTRAINT hrm_payroll_generated_by_fkey FOREIGN KEY (generated_by) REFERENCES public.hrm_users(id);


--
-- Name: hrm_payroll_ot_summary hrm_payroll_ot_summary_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_ot_summary
    ADD CONSTRAINT hrm_payroll_ot_summary_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_payroll_ot_summary hrm_payroll_ot_summary_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_payroll_ot_summary
    ADD CONSTRAINT hrm_payroll_ot_summary_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.hrm_employee(id) ON DELETE CASCADE;


--
-- Name: hrm_tenant_configuration hrm_tenant_configuration_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_tenant_configuration
    ADD CONSTRAINT hrm_tenant_configuration_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.hrm_tenant(id) ON DELETE CASCADE;


--
-- Name: hrm_user_role_mapping hrm_user_role_mapping_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_user_role_mapping
    ADD CONSTRAINT hrm_user_role_mapping_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.hrm_company(id) ON DELETE CASCADE;


--
-- Name: hrm_user_role_mapping hrm_user_role_mapping_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_user_role_mapping
    ADD CONSTRAINT hrm_user_role_mapping_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.hrm_roles(id) ON DELETE CASCADE;


--
-- Name: hrm_user_role_mapping hrm_user_role_mapping_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_user_role_mapping
    ADD CONSTRAINT hrm_user_role_mapping_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.hrm_users(id) ON DELETE CASCADE;


--
-- Name: hrm_users hrm_users_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_users
    ADD CONSTRAINT hrm_users_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organization(id);


--
-- Name: hrm_users hrm_users_reporting_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_users
    ADD CONSTRAINT hrm_users_reporting_manager_id_fkey FOREIGN KEY (reporting_manager_id) REFERENCES public.hrm_users(id) ON DELETE SET NULL;


--
-- Name: hrm_users hrm_users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_users
    ADD CONSTRAINT hrm_users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.hrm_roles(id);


--
-- Name: hrm_work_schedules hrm_work_schedules_working_hours_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hrm_work_schedules
    ADD CONSTRAINT hrm_work_schedules_working_hours_id_fkey FOREIGN KEY (working_hours_id) REFERENCES public.hrm_working_hours(id);


--
-- PostgreSQL database dump complete
--

