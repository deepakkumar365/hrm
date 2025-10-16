-- SQL script to add missing designation_id column to hrm_employee table
-- Execute this in your PostgreSQL database

-- Step 1: Add the column
ALTER TABLE hrm_employee 
ADD COLUMN designation_id INTEGER;

-- Step 2: Add foreign key constraint
ALTER TABLE hrm_employee 
ADD CONSTRAINT fk_hrm_employee_designation_id 
FOREIGN KEY (designation_id) REFERENCES hrm_designation(id);