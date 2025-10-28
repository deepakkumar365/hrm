-- ============================================
-- HRM DATABASE EXPORT - ALL TABLES DATA
-- Exported: 2025-10-29 01:20:58
-- ============================================


-- ============================================
-- TABLE: ROLE (4 rows)
-- ============================================
INSERT INTO role (id, name, description, created_at, updated_at, is_active) VALUES
  (1, 'Super Admin', 'Super administrator with all permissions.', '2025-09-30T17:25:16.235173', '2025-09-30T23:05:53.904892', TRUE),
  (2, 'Tenant Admin', 'Administrator with organization-wide permissions.', '2025-09-30T17:25:16.785113', '2025-10-15T11:35:39.046738', TRUE),
  (3, 'HR Manager', 'HR manager with employee management permissions.', '2025-09-30T17:25:17.318494', '2025-10-15T11:24:26.467218', TRUE),
  (4, 'User', 'Regular employee with limited permissions.', '2025-09-30T17:25:17.853726', '2025-09-30T23:05:55.830709', TRUE);



-- ============================================
-- TABLE: HRM_TENANT (1 rows)
-- ============================================
INSERT INTO hrm_tenant (id, name, code, description, is_active, created_by, created_at, modified_by, modified_at, country_code, currency_code) VALUES
  ('a4c3e2ed-cfac-47ca-8a51-0a5becb1a12d', 'AKS Group of Companies', 'AKS25', 'AKS Group of Companies - Singapore', TRUE, 'admin@noltrion.com', '2025-10-07T17:22:23.026721+00:00', 'superadmin@hrm.com', '2025-10-15T10:30:35.340725+00:00', 'SG', 'SGD');



-- ============================================
-- TABLE: HRM_COMPANY (2 rows)
-- ============================================
INSERT INTO hrm_company (id, tenant_id, name, code, description, address, uen, registration_number, tax_id, phone, email, website, logo_path, is_active, created_by, created_at, modified_by, modified_at) VALUES
  ('7c725fc2-2dfd-45b0-aa5b-55ca1a054652', 'a4c3e2ed-cfac-47ca-8a51-0a5becb1a12d', 'AKS BUSINESS SOLUTIONS PTE LTD', 'AKSB', 'AKS BUSINESS SOLUTIONS PTE LTD', '71 Woodlands Industrial Park E9 #03-01 ', '202402639Z', NULL, NULL, '', '', 'https://aksgroup.com.sg', NULL, TRUE, 'admin@noltrion.com', '2025-10-07T17:27:42.711775+00:00', NULL, NULL),
  ('8b28e2c2-7bb4-4998-a9d9-66a722d7c746', 'a4c3e2ed-cfac-47ca-8a51-0a5becb1a12d', 'AKS LOGISTICS PTE LTD', 'AKSL', 'AKS LOGISTICS PTE LTD', '71 Woodlands Industrial Park E9 #03-01 ', '201716172K', NULL, NULL, '', 'aks@gmail.com', 'https://aksgroup.com.sg/', NULL, TRUE, 'admin@noltrion.com', '2025-10-07T17:25:52.079766+00:00', NULL, NULL);



-- ============================================
-- TABLE: ORGANIZATION (1 rows)
-- ============================================
INSERT INTO organization (id, name, created_at, modified_at, logo_path, address, uen, tenant_id, created_by, modified_by) VALUES
  (1, 'AKS LOGISTICS PTE LTD', '2025-09-30T17:25:19.218404', '2025-10-21T21:21:56.591660', 'logos/company_logo.svg', '71 Woodlands Industrial Park E9 #03-01 ,Singapore 757048', '201716172K', 'a4c3e2ed-cfac-47ca-8a51-0a5becb1a12d', 'system', NULL);



-- ============================================
-- TABLE: HRM_USERS (8 rows)
-- ============================================
INSERT INTO hrm_users (id, username, email, password_hash, first_name, last_name, is_active, must_reset_password, organization_id, role_id, reporting_manager_id, created_at, updated_at) VALUES
  (9, 'superadmin', 'superadmin@hrm.com', 'scrypt:32768:8:1$pW0mqDwEQ5xgAVDp$42ef87225e2e036ae773de95f048bb48cca146bf226767234139622828ed825af853de68fc8bb11403d67755745dd81782eeaf2aca7d88a66716efe0c5e3d306', 'Super', 'Admin', TRUE, FALSE, 1, 1, NULL, '2025-10-08T20:50:51.467542', '2025-10-08T20:50:51.467542'),
  (10, 'tenantadmin', 'tenantadmin@hrm.com', 'scrypt:32768:8:1$hTmM6tiRI7j6y7rD$d5a23f9d82f47f80b5a78f9bdcc5ec9174c6001d472dd1785336d103b1045cbf09177494a7265f76d0117fd62392062f444aa248da6906aa9ce326ecb22806ee', 'Tenant', 'Admin', TRUE, FALSE, 1, 2, NULL, '2025-10-08T20:50:52.173852', '2025-10-08T20:50:52.173852'),
  (11, 'manager', 'manager@hrm.com', 'scrypt:32768:8:1$iDOh5DSb9st8Wrs6$c65f767b52f88cddac95a2907455e47403713b918d32a0d31eacac0a1c516347d2840e9b0b62e8dd8367b303ecfb3fcd0d2a8251302bd167e41daf58c8acead2', 'Team', 'Manager', TRUE, FALSE, 1, 3, NULL, '2025-10-08T20:50:52.886030', '2025-10-08T20:50:52.886030'),
  (12, 'employee', 'employee@hrm.com', 'scrypt:32768:8:1$yxTL2dxUzx7psf2M$870e2bf687f581ccfdfa79285d889a795eab27338a3b3d707afd6ee52967158acfbe013cd42cc0e52138b6850893778aa30f36b16b45270da7bad923ed153fbc', 'Regular', 'Employee', TRUE, FALSE, 1, 4, 12, '2025-10-08T20:50:53.571819', '2025-10-08T20:50:53.571819'),
  (13, 'nagarajan.manoharan', 'nagarajsethu118@gmail.com', 'scrypt:32768:8:1$gLfyamwMmq3PNLdJ$25ce77eaae2fb9981ba9e00c20abef9f545ce8ee25e8cf5f23d9a2b37e8e5632f7157e7cbd9fda73fc60184dac2af2d2504c62e23eead68c03be2445f48afff1', 'NAGARAJAN', 'MANOHARAN', TRUE, TRUE, 1, 4, NULL, '2025-10-12T13:25:53.480634', '2025-10-12T13:26:18.877967'),
  (75, 'abc.ndnd', '', 'scrypt:32768:8:1$ODnNXXzY2CFblytP$8c89ffc83c968728119f69f9eeffb161e48ee7db46ef0703773e206652d94095bfdb62f9a432c5dd87903e3d4c6f238b5b19381b81e21226cabb54d6e63383c7', 'abc', 'ndnd', TRUE, TRUE, 1, 4, NULL, '2025-10-21T19:57:58.268539', '2025-10-22T09:32:06.310883'),
  (76, 'senthil.hr', 'SENTHIL@GMAIL.COM', 'scrypt:32768:8:1$FfcbcHNNFG18JioM$7c6da9624127afce4a0f864bdd8d1a57f601ebd50b616dcaa7cede494403d9598430042553c9a47f8403640c955eb18700e592d90c873b73b017ad80fbb437d1', 'senthil', 'HR', TRUE, TRUE, 1, 3, NULL, '2025-10-22T10:05:42.107247', '2025-10-22T10:05:42.107252'),
  (77, 'shalini.hr', 'shalin@gmail.com', 'scrypt:32768:8:1$kPHNZDRKPOwvjYCb$2c70571bb23aaf22592427c1df0a7349f8c65d965010ceb945881816a9cd45a6e8d4e8deca14e7d3f261b9ffbe32fd0d6ef2e1fc329203656a3f4ce6f3e21867', 'Shalini', 'HR', TRUE, TRUE, 1, 3, NULL, '2025-10-22T10:08:51.201381', '2025-10-22T10:08:51.201385');



-- ============================================
-- TABLE: HRM_EMPLOYEE (14 rows)
-- ============================================
INSERT INTO hrm_employee (id, employee_id, first_name, last_name, email, phone, nric, date_of_birth, gender, nationality, address, postal_code, profile_image_path, position, department, hire_date, employment_type, work_permit_type, work_permit_expiry, basic_salary, allowances, hourly_rate, cpf_account, employee_cpf_rate, employer_cpf_rate, bank_name, bank_account, account_holder_name, swift_code, ifsc_code, is_active, termination_date, user_id, organization_id, manager_id, working_hours_id, work_schedule_id, created_at, modified_at, company_id, created_by, modified_by, father_name, work_permit_number, timezone, location, designation_id, overtime_group_id) VALUES
  (2, 'EMP20251001003051', 'Sashikumar', 'Asogan', 'sasogan@noltrion.com', '', 'S8623537D', '1986-08-22', 'Male', 'Singaporean', '688C WOODLANDS DRIVE 75 #09-42 S''PRE 733688', '', 'uploads/employees/EMP20251001003051_1759258851.jpg', 'Manager', 'Operations', '1993-08-26', 'Full-time', 'Citizen', NULL, '1600.00', '1600.00', '0.00', '', '20.00', '17.00', '', '', 'Sashikumar Asogan', '', '', TRUE, NULL, NULL, 1, NULL, 3, NULL, '2025-10-01T00:30:51.072213', '2025-10-08T15:21:10.850152', NULL, 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (3, 'EMP20251006090841', 'Shalini', 'Suraesh', 'Shalini@akslogistics.com', '', 'S9933141J', '1999-10-09', 'Female', 'Singaporean', 'BLK 203 PETIR ROAD #03-673 S''PRE 6702023', '6702023', 'uploads/employees/EMP20251006090841_1759741721.png', 'Manager', 'Administration', '2025-01-01', 'Full-time', 'Citizen', NULL, '1600.00', '0.00', '10.00', '', '20.00', '17.00', '', '', 'Shalini Suraesh', '', '', TRUE, NULL, NULL, 1, 2, 4, 1, '2025-10-06T09:08:41.532182', '2025-10-08T15:21:10.850152', NULL, 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (4, 'EMP20251006092249', 'Ram Kumar', 'Murugasu', 'RamKumar@aks.com', '', 'S8125113D', '1981-08-08', 'Male', 'Singaporean', 'BLK 473A UPPER SERANGOON CRESCENT #02-307 S''PRE 531473', '531473', 'uploads/employees/EMP20251006092249_1759742569.png', 'Manager', 'Administration', '2023-01-01', 'Full-time', 'Citizen', NULL, '1750.00', '0.00', '10.00', '', '20.00', '17.00', '', '', 'Ram Kumar', '', '', TRUE, NULL, NULL, 1, 2, 4, 1, '2025-10-06T09:22:49.668031', '2025-10-08T15:21:10.850152', NULL, 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (5, 'EMP20251006094007', 'Neelakanan', 'Suparamaniam', 'Neelakanan@aks.com', '', 'S8231403B', '1982-08-23', 'Male', 'Singaporean', '661 Woodlands Ring Road #03-158 S''PRE 730661', '730661', 'uploads/employees/EMP20251006094007_1759743607.png', 'User', 'Operations', '2023-01-01', 'Full-time', 'Citizen', NULL, '1600.00', '0.00', '9.09', '', '20.00', '17.00', '', '', 'Neelakanan', '', '', TRUE, NULL, NULL, 1, 2, 1, 1, '2025-10-06T09:40:07.610202', '2025-10-08T15:21:10.850152', NULL, 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (6, 'EMP20251007150050', 'Muhammad Hafiz', 'Bin Kamsan', 'MuhammadHafiz@gmail.com', '', 'S9010625B', '1990-03-26', 'Male', 'Singaporean', 'BLK 329 BUKIT BATOK STREET 33 #08-91 S''PRE 650329', '650329', 'uploads/employees/EMP20251007150050_1759849250.png', 'User', 'Operations', '2023-01-01', 'Full-time', 'Citizen', NULL, '1600.00', '0.00', '9.09', '', '20.00', '17.00', '', '', 'Muhammad Hafiz', '', '', TRUE, NULL, NULL, 1, 2, 1, 1, '2025-10-07T15:00:50.083931', '2025-10-08T15:21:10.850152', '7c725fc2-2dfd-45b0-aa5b-55ca1a054652', 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (7, 'EMP20251007154417', 'Ang Chye ', 'Hock Andrw', 'HOCKANDREW@gmail.com', '', 'S1701093Z', '2025-10-07', 'Male', 'Singaporean', 'BLK 329 BUKIT BATOK STREET 33 #08-91 S''PRE 650329', '650329', 'uploads/employees/EMP20251007154417_1759851857.png', 'Admin', 'Administration', '2025-10-01', 'Full-time', 'Citizen', NULL, '1600.00', '0.00', '9.09', '', '20.00', '17.00', '', '', 'HOCK ANDREW', '', '', TRUE, NULL, NULL, 1, 2, 1, 1, '2025-10-07T15:44:17.751829', '2025-10-21T19:34:12.980371', '7c725fc2-2dfd-45b0-aa5b-55ca1a054652', 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (10, 'EMP0009', 'Super', 'Admin', 'superadmin@hrm.com', '+65 9000 0000', 'S0000009A', NULL, NULL, NULL, NULL, NULL, NULL, 'System Administrator', 'Information Technology', '2025-10-09', NULL, NULL, NULL, '3000.00', '0.00', NULL, NULL, '20.00', '17.00', NULL, NULL, NULL, NULL, NULL, TRUE, NULL, 9, 1, NULL, NULL, NULL, '2025-10-09T11:19:44.965460', '2025-10-09T11:19:44.965460', '8b28e2c2-7bb4-4998-a9d9-66a722d7c746', 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (11, 'EMP0010', 'Tenant', 'Admin', 'tenantadmin@hrm.com', '+65 9000 0000', 'S0000010A', NULL, '', '', 'None', 'None', NULL, 'Accountant', 'Information Technology', '2025-10-09', 'Full-time', 'Citizen', NULL, '3000.00', '0.00', NULL, 'None', '20.00', '17.00', NULL, NULL, NULL, NULL, NULL, TRUE, NULL, 10, 1, NULL, NULL, NULL, '2025-10-09T11:19:45.724548', '2025-10-21T19:16:11.976901', '8b28e2c2-7bb4-4998-a9d9-66a722d7c746', 'system', NULL, NULL, NULL, 'UTC', NULL, 9, NULL),
  (12, 'EMP0011', 'Team', 'Manager', 'manager@hrm.com', '+65 9000 0000', 'S0000011A', NULL, '', '', 'None', 'None', NULL, 'HR Manager', 'Information Technology', '2025-10-09', 'Full-time', 'Citizen', NULL, '3000.00', '0.00', NULL, 'None', '20.00', '17.00', NULL, NULL, NULL, NULL, NULL, TRUE, NULL, 11, 1, NULL, NULL, NULL, '2025-10-09T11:19:46.628876', '2025-10-16T02:29:52.982902', '8b28e2c2-7bb4-4998-a9d9-66a722d7c746', 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (13, 'EMP0012', 'Regular', 'Employee', 'employee@hrm.com', '+65 9000 0000', 'S0000012A', NULL, NULL, NULL, NULL, NULL, NULL, 'Staff Member', 'Information Technology', '2025-10-09', NULL, NULL, NULL, '3000.00', '0.00', NULL, NULL, '20.00', '17.00', NULL, NULL, NULL, NULL, NULL, TRUE, NULL, 12, 1, 12, NULL, NULL, '2025-10-09T11:19:47.144681', '2025-10-18T19:04:56.360664', '8b28e2c2-7bb4-4998-a9d9-66a722d7c746', 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (14, 'EMP20251012132552', 'Nagarajan', 'Manoharan', 'nagarajsethu118@gmail.com', '09095030250', 'S0000012C', '2025-10-12', '', '', 'No 89 MKB NAGAR 14TH EAST CROSS STREETVYASARPADI CHENNAI', '600039', 'uploads/employees/EMP20251012132552_1760275552.png', 'User', '', '2025-10-12', 'Full-time', 'Citizen', NULL, '1000.00', '0.00', '0.01', '', '20.00', '17.00', NULL, NULL, NULL, NULL, NULL, TRUE, NULL, 13, 1, NULL, NULL, NULL, '2025-10-12T13:25:52.648826', '2025-10-21T19:34:12.980371', '7c725fc2-2dfd-45b0-aa5b-55ca1a054652', 'system', NULL, NULL, NULL, 'UTC', NULL, NULL, NULL),
  (80, 'EMP20251021195754', 'abc', 'ndnd', '', '', 'S9535230H', NULL, '', '', '', '', 'uploads/employees/EMP20251021195754_1761056875.png', 'Driver', '', '2025-10-01', 'Full-time', 'Citizen', NULL, '1600.00', '0.00', '0.00', '', '20.00', '17.00', NULL, NULL, NULL, NULL, NULL, TRUE, NULL, 75, 1, 2, NULL, NULL, '2025-10-21T19:57:55.344316', '2025-10-21T14:27:59.426097', '8b28e2c2-7bb4-4998-a9d9-66a722d7c746', 'system', NULL, NULL, NULL, 'UTC', NULL, 3, NULL),
  (83, 'EMP20251022100541', 'senthil', 'HR', 'SENTHIL@GMAIL.COM', '', 'G2921225U', NULL, '', '', '', '', 'uploads/employees/EMP20251022100541_1761127541.png', 'Operations Manager', '', '2025-06-01', 'Full-time', 'Employment Pass', NULL, '2000.00', '0.00', '0.01', '', '20.00', '17.00', NULL, NULL, NULL, NULL, NULL, TRUE, NULL, 76, 1, 2, NULL, NULL, '2025-10-22T10:05:41.269367', '2025-10-22T10:05:42.211950', '7c725fc2-2dfd-45b0-aa5b-55ca1a054652', 'system', NULL, NULL, NULL, 'UTC', NULL, 13, NULL),
  (84, 'EMP20251022100849', 'Shalini', 'HR', 'shalin@gmail.com', '', 'G2200906R', NULL, '', '', '', '', 'uploads/employees/EMP20251022100849_1761127729.png', 'Operations Manager', '', '2025-05-01', 'Full-time', 'Employment Pass', NULL, '2000.00', '0.00', '0.01', '', '20.00', '17.00', NULL, NULL, NULL, NULL, NULL, TRUE, NULL, 77, 1, NULL, NULL, NULL, '2025-10-22T10:08:49.568401', '2025-10-22T10:08:51.298474', '7c725fc2-2dfd-45b0-aa5b-55ca1a054652', 'system', NULL, NULL, NULL, 'UTC', NULL, 13, NULL);



-- ============================================
-- TABLE: HRM_DESIGNATION (25 rows)
-- ============================================
INSERT INTO hrm_designation (id, name, description, is_active, created_at, updated_at, created_by, modified_by) VALUES
  (1, 'Director', 'Director', TRUE, '2025-10-16T12:19:05.665498', '2025-10-16T12:19:05.665498', 'system', NULL),
  (2, 'Manager', 'Manager', TRUE, '2025-10-16T12:19:06.137339', '2025-10-16T12:19:06.137339', 'system', NULL),
  (3, 'Driver', 'Driver', TRUE, '2025-10-16T12:19:06.613877', '2025-10-16T12:19:06.613877', 'system', NULL),
  (4, 'Vehicle Attendant', 'Vehicle Attendant', TRUE, '2025-10-16T12:19:07.109824', '2025-10-16T12:19:07.109824', 'system', NULL),
  (5, 'Velder and Flame Cutter', 'Velder and Flame Cutter', TRUE, '2025-10-16T12:19:07.580507', '2025-10-16T12:19:07.580507', 'system', NULL),
  (6, 'HR Manager', 'HR Manager', TRUE, '2025-10-16T12:19:08.076482', '2025-10-16T12:19:08.076482', 'system', NULL),
  (7, 'HR Executive', 'HR Executive', TRUE, '2025-10-16T12:19:08.547423', '2025-10-16T12:19:08.547423', 'system', NULL),
  (8, 'Finance Manager', 'Finance Manager', TRUE, '2025-10-16T12:19:09.059004', '2025-10-16T12:19:09.059004', 'system', NULL),
  (9, 'Accountant', 'Accountant', TRUE, '2025-10-16T12:19:09.547275', '2025-10-16T12:19:09.547275', 'system', NULL),
  (10, 'Sales Manager', 'Sales Manager', TRUE, '2025-10-16T12:19:10.018932', '2025-10-16T12:19:10.018932', 'system', NULL),
  (11, 'Sales Executive', 'Sales Executive', TRUE, '2025-10-16T12:19:10.488567', '2025-10-16T12:19:10.488567', 'system', NULL),
  (12, 'Business Development Manager', 'Business Development Manager', TRUE, '2025-10-16T12:19:10.959250', '2025-10-16T12:19:10.959250', 'system', NULL),
  (13, 'Operations Manager', 'Operations Manager', TRUE, '2025-10-16T12:19:11.456065', '2025-10-16T12:19:11.456065', 'system', NULL),
  (14, 'Operations Executive', 'Operations Executive', TRUE, '2025-10-16T12:19:11.931348', '2025-10-16T12:19:11.931348', 'system', NULL),
  (15, 'Marketing Manager', 'Marketing Manager', TRUE, '2025-10-16T12:19:12.400934', '2025-10-16T12:19:12.400934', 'system', NULL),
  (16, 'Marketing Specialist', 'Marketing Specialist', TRUE, '2025-10-16T12:19:12.872446', '2025-10-16T12:19:12.872446', 'system', NULL),
  (17, 'Business Analyst', 'Business Analyst', TRUE, '2025-10-16T12:19:13.340219', '2025-10-16T12:19:13.340219', 'system', NULL),
  (18, 'Data Analyst', 'Data Analyst', TRUE, '2025-10-16T12:19:13.814688', '2025-10-16T12:19:13.814688', 'system', NULL),
  (19, 'Quality Assurance Lead', 'Quality Assurance Lead', TRUE, '2025-10-16T12:19:14.302590', '2025-10-16T12:19:14.302590', 'system', NULL),
  (20, 'Quality Assurance Engineer', 'Quality Assurance Engineer', TRUE, '2025-10-16T12:19:14.769737', '2025-10-16T12:19:14.769737', 'system', NULL),
  (21, 'DevOps Engineer', 'DevOps Engineer', TRUE, '2025-10-16T12:19:15.253688', '2025-10-16T12:19:15.253688', 'system', NULL),
  (22, 'System Administrator', 'System Administrator', TRUE, '2025-10-16T12:19:15.723830', '2025-10-16T12:19:15.723830', 'system', NULL),
  (23, 'Network Administrator', 'Network Administrator', TRUE, '2025-10-16T12:19:16.192552', '2025-10-16T12:19:16.192552', 'system', NULL),
  (24, 'Database Administrator', 'Database Administrator', TRUE, '2025-10-16T12:19:16.677979', '2025-10-16T12:19:16.677979', 'system', NULL),
  (25, 'Support Engineer', 'Support Engineer', TRUE, '2025-10-16T12:19:17.157313', '2025-10-16T12:19:17.157313', 'system', NULL);



-- ============================================
-- TABLE: HRM_WORKING_HOURS (4 rows)
-- ============================================
INSERT INTO hrm_working_hours (id, name, hours_per_day, hours_per_week, description, is_active, created_at, updated_at) VALUES
  (1, 'Full-time Standard', '8.00', '40.00', 'Standard full-time working hours', TRUE, '2025-09-30T17:29:41.632988', '2025-09-30T17:29:41.632988'),
  (2, 'Part-time (Half Day)', '4.00', '20.00', 'Half day part-time schedule', TRUE, '2025-09-30T17:29:41.632988', '2025-09-30T17:29:41.632988'),
  (3, 'Extended Hours', '9.00', '45.00', 'Extended working hours with overtime', TRUE, '2025-09-30T17:29:41.632988', '2025-09-30T17:29:41.632988'),
  (4, 'Flexible Hours', '8.00', '40.00', 'Flexible working arrangement', TRUE, '2025-09-30T17:29:41.632988', '2025-09-30T17:29:41.632988');



-- ============================================
-- TABLE: HRM_WORK_SCHEDULES (4 rows)
-- ============================================
INSERT INTO hrm_work_schedules (id, name, start_time, end_time, break_duration, description, is_active, created_at, updated_at) VALUES
  (1, 'Standard Hours', '09:00:00', '18:00:00', 60, 'Standard 9-to-6 schedule', TRUE, '2025-09-30T17:29:42.172685', '2025-09-30T17:29:42.172685'),
  (2, 'Early Shift', '07:00:00', '16:00:00', 60, 'Early morning shift', TRUE, '2025-09-30T17:29:42.172685', '2025-09-30T17:29:42.172685'),
  (3, 'Late Shift', '14:00:00', '23:00:00', 60, 'Afternoon to evening shift', TRUE, '2025-09-30T17:29:42.172685', '2025-09-30T17:29:42.172685'),
  (4, 'Flexible Hours', '08:00:00', '17:00:00', 60, 'Flexible timing schedule', TRUE, '2025-09-30T17:29:42.172685', '2025-09-30T17:29:42.172685');


-- Table 'hrm_employee_bank_info' is empty


-- Table 'hrm_employee_documents' is empty



-- ============================================
-- TABLE: HRM_PAYROLL (8 rows)
-- ============================================
INSERT INTO hrm_payroll (id, employee_id, pay_period_start, pay_period_end, basic_pay, overtime_pay, allowances, bonuses, gross_pay, employee_cpf, employer_cpf, income_tax, other_deductions, net_pay, days_worked, overtime_hours, leave_days, status, generated_by, generated_at, absent_days, lop_days, lop_deduction) VALUES
  (7, 80, '2025-09-01', '2025-09-30', '1600.00', '0.00', '0.00', '0.00', '1600.00', '320.00', '272.00', '0.00', '0.00', '1280.00', 4, '0.00', 0, 'Draft', 10, '2025-10-22T02:59:51.353112', 0, 0, '0.00'),
  (8, 13, '2025-07-01', '2025-07-31', '3000.00', '0.00', '0.00', '0.00', '3000.00', '600.00', '510.00', '0.00', '0.00', '2400.00', 2, '0.00', 0, 'Draft', 11, '2025-10-22T02:53:37.386801', 0, 0, '0.00'),
  (9, 10, '2025-07-01', '2025-07-31', '3000.00', '0.00', '200.00', '0.00', '3200.00', '640.00', '544.00', '0.00', '0.00', '2560.00', 2, '0.00', 0, 'Draft', 11, '2025-10-22T03:04:51.190423', 0, 0, '0.00'),
  (10, 80, '2025-10-01', '2025-10-31', '1600.00', '0.00', '0.00', '0.00', '1600.00', '320.00', '272.00', '0.00', '0.00', '1280.00', 7, '0.00', 0, 'Draft', 10, '2025-10-22T09:39:33.534595', 0, 0, '0.00'),
  (11, 12, '2025-10-01', '2025-10-31', '3000.00', '0.00', '0.00', '0.00', '3000.00', '600.00', '510.00', '0.00', '0.00', '2400.00', 8, '0.00', 0, 'Draft', 10, '2025-10-22T09:39:33.681227', 0, 0, '0.00'),
  (12, 13, '2025-10-01', '2025-10-31', '3000.00', '0.00', '0.00', '0.00', '3000.00', '600.00', '510.00', '0.00', '0.00', '2400.00', 8, '0.00', 0, 'Draft', 10, '2025-10-22T09:39:33.873885', 0, 0, '0.00'),
  (13, 10, '2025-10-01', '2025-10-31', '3000.00', '0.00', '400.00', '0.00', '3400.00', '680.00', '578.00', '0.00', '0.00', '2720.00', 8, '0.00', 0, 'Draft', 10, '2025-10-22T09:40:14.430652', 0, 0, '0.00'),
  (14, 11, '2025-10-01', '2025-10-31', '3000.00', '0.00', '0.00', '0.00', '3000.00', '600.00', '510.00', '0.00', '0.00', '2400.00', 8, '0.00', 0, 'Draft', 10, '2025-10-22T09:40:14.565916', 0, 0, '0.00');



-- ============================================
-- TABLE: HRM_PAYROLL_CONFIGURATION (14 rows)
-- ============================================
INSERT INTO hrm_payroll_configuration (id, employee_id, allowance_1_name, allowance_1_amount, allowance_2_name, allowance_2_amount, allowance_3_name, allowance_3_amount, allowance_4_name, allowance_4_amount, ot_rate_per_hour, created_at, updated_at, updated_by, employer_cpf, employee_cpf, net_salary, remarks, levy_allowance_name, levy_allowance_amount) VALUES
  (12, 10, 'Transport Allowance', '200.00', 'Housing Allowance', '200.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:07.359056', '2025-10-22T09:34:59.362067', 10, '0', '0', '0', NULL, NULL, '0.00'),
  (13, 11, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:07.965275', '2025-10-21T18:51:07.965286', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (14, 12, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:08.479237', '2025-10-21T18:51:08.479250', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (15, 13, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:09.092838', '2025-10-21T18:51:09.092856', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (16, 2, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:09.705836', '2025-10-22T02:47:49.753370', 11, '0', '0', '0', NULL, NULL, '0.00'),
  (17, 3, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:10.418600', '2025-10-21T18:51:10.418610', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (18, 4, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:11.037787', '2025-10-21T18:51:11.037799', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (19, 5, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:11.854497', '2025-10-21T18:51:11.854504', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (20, 6, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:12.423588', '2025-10-21T18:51:12.423605', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (21, 7, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T18:51:13.084263', '2025-10-21T18:51:13.084279', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (22, 14, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T21:08:00.384484', '2025-10-21T21:08:00.384505', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (23, 80, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-21T21:08:00.983268', '2025-10-21T21:08:00.983278', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (24, 83, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-22T22:50:44.199432', '2025-10-22T22:50:44.199436', NULL, '0', '0', '0', NULL, NULL, '0.00'),
  (25, 84, 'Transport Allowance', '0.00', 'Housing Allowance', '0.00', 'Meal Allowance', '0.00', 'Other Allowance', '0.00', NULL, '2025-10-22T22:50:44.256852', '2025-10-22T22:50:44.256856', NULL, '0', '0', '0', NULL, NULL, '0.00');



-- ============================================
-- TABLE: HRM_ATTENDANCE (270 rows)
-- ============================================
INSERT INTO hrm_attendance (id, employee_id, date, clock_in, clock_out, break_start, break_end, regular_hours, overtime_hours, total_hours, status, remarks, location_lat, location_lng, created_at, updated_at, has_overtime, overtime_approved, overtime_approved_by, overtime_approved_at, lop) VALUES
  (29, 80, '2025-10-21', NULL, NULL, NULL, NULL, '4.00', '0.00', '4.00', 'Half Day', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:09.400740', '2025-10-22T09:14:35.897709', FALSE, NULL, NULL, NULL, FALSE),
  (30, 7, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:10.001486', '2025-10-21T20:47:03.452583', FALSE, NULL, NULL, NULL, FALSE),
  (31, 6, '2025-10-21', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:11.028856', '2025-10-22T09:14:47.183621', FALSE, NULL, NULL, NULL, FALSE),
  (32, 14, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:11.948320', '2025-10-21T20:47:06.806619', FALSE, NULL, NULL, NULL, FALSE),
  (33, 5, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:12.564768', '2025-10-21T20:47:01.995551', FALSE, NULL, NULL, NULL, FALSE),
  (34, 4, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:13.279623', '2025-10-21T20:47:01.212667', FALSE, NULL, NULL, NULL, FALSE),
  (35, 13, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:14.189395', '2025-10-21T20:47:04.861445', FALSE, NULL, NULL, NULL, FALSE),
  (36, 2, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:15.123393', '2025-10-21T20:46:59.740658', FALSE, NULL, NULL, NULL, FALSE),
  (37, 3, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:16.103086', '2025-10-21T20:47:00.459953', FALSE, NULL, NULL, NULL, FALSE),
  (38, 10, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:17.068635', '2025-10-21T20:47:05.475763', FALSE, NULL, NULL, NULL, FALSE),
  (39, 12, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:18.091957', '2025-10-21T20:47:04.146819', FALSE, NULL, NULL, NULL, FALSE),
  (40, 11, '2025-10-21', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T20:31:19.116539', '2025-10-21T20:47:06.193457', FALSE, NULL, NULL, NULL, FALSE),
  (41, 80, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:47:55.759802', '2025-10-21T20:47:55.759816', FALSE, NULL, NULL, NULL, FALSE),
  (42, 7, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:47:56.368629', '2025-10-21T20:47:56.368640', FALSE, NULL, NULL, NULL, FALSE),
  (43, 6, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:47:56.984028', '2025-10-21T20:47:56.984041', FALSE, NULL, NULL, NULL, FALSE),
  (44, 14, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:47:57.596658', '2025-10-21T20:47:57.596665', FALSE, NULL, NULL, NULL, FALSE),
  (45, 5, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:47:58.211917', '2025-10-21T20:47:58.211930', FALSE, NULL, NULL, NULL, FALSE),
  (46, 4, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:47:58.825055', '2025-10-21T20:47:58.825062', FALSE, NULL, NULL, NULL, FALSE),
  (47, 13, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:47:59.440869', '2025-10-21T20:47:59.440883', FALSE, NULL, NULL, NULL, FALSE),
  (48, 2, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:00.012023', '2025-10-21T20:48:00.012031', FALSE, NULL, NULL, NULL, FALSE),
  (49, 3, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:00.567705', '2025-10-21T20:48:00.567717', FALSE, NULL, NULL, NULL, FALSE),
  (50, 10, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:01.182273', '2025-10-21T20:48:01.182284', FALSE, NULL, NULL, NULL, FALSE),
  (51, 12, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:01.832659', '2025-10-21T20:48:01.832674', FALSE, NULL, NULL, NULL, FALSE),
  (52, 11, '2025-10-20', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:02.408989', '2025-10-21T20:48:02.408997', FALSE, NULL, NULL, NULL, FALSE),
  (53, 80, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:38.454339', '2025-10-21T20:48:38.454355', FALSE, NULL, NULL, NULL, FALSE),
  (54, 7, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:39.174961', '2025-10-21T20:48:39.174974', FALSE, NULL, NULL, NULL, FALSE),
  (55, 6, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:39.690220', '2025-10-21T20:48:39.690240', FALSE, NULL, NULL, NULL, FALSE),
  (56, 14, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:40.296019', '2025-10-21T20:48:40.296027', FALSE, NULL, NULL, NULL, FALSE),
  (57, 5, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:40.911716', '2025-10-21T20:48:40.911726', FALSE, NULL, NULL, NULL, FALSE),
  (58, 4, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:41.747931', '2025-10-21T20:48:41.747947', FALSE, NULL, NULL, NULL, FALSE),
  (59, 13, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:42.422663', '2025-10-21T20:48:42.422679', FALSE, NULL, NULL, NULL, FALSE),
  (60, 2, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:43.141845', '2025-10-21T20:48:43.141855', FALSE, NULL, NULL, NULL, FALSE),
  (61, 3, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:43.882904', '2025-10-21T20:48:43.882920', FALSE, NULL, NULL, NULL, FALSE),
  (62, 10, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:44.495593', '2025-10-21T20:48:44.495604', FALSE, NULL, NULL, NULL, FALSE),
  (63, 12, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:45.109511', '2025-10-21T20:48:45.109525', FALSE, NULL, NULL, NULL, FALSE),
  (64, 11, '2025-10-16', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T20:48:45.724549', '2025-10-21T20:48:45.724567', FALSE, NULL, NULL, NULL, FALSE),
  (65, 80, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:46.041385', '2025-10-21T21:07:23.616255', FALSE, NULL, NULL, NULL, FALSE),
  (66, 7, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:46.642637', '2025-10-21T21:07:27.333241', FALSE, NULL, NULL, NULL, FALSE),
  (67, 6, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:47.263371', '2025-10-21T21:07:26.687087', FALSE, NULL, NULL, NULL, FALSE),
  (68, 14, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:47.870970', '2025-10-21T21:07:30.366222', FALSE, NULL, NULL, NULL, FALSE),
  (69, 5, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:48.455995', '2025-10-21T21:07:26.064760', FALSE, NULL, NULL, NULL, FALSE),
  (70, 4, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:49.105536', '2025-10-21T21:07:25.460196', FALSE, NULL, NULL, NULL, FALSE),
  (71, 13, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:49.713909', '2025-10-21T21:07:28.466107', FALSE, NULL, NULL, NULL, FALSE),
  (72, 2, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:50.328487', '2025-10-21T21:07:24.222785', FALSE, NULL, NULL, NULL, FALSE),
  (73, 3, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:50.944448', '2025-10-21T21:07:24.853043', FALSE, NULL, NULL, NULL, FALSE),
  (74, 10, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:51.555899', '2025-10-21T21:07:29.140061', FALSE, NULL, NULL, NULL, FALSE),
  (75, 12, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:52.171293', '2025-10-21T21:07:27.944863', FALSE, NULL, NULL, NULL, FALSE),
  (76, 11, '2025-10-09', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T21:06:52.784098', '2025-10-21T21:07:29.751855', FALSE, NULL, NULL, NULL, FALSE),
  (77, 80, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:00.921502', '2025-10-21T17:21:00.921506', FALSE, NULL, NULL, NULL, FALSE),
  (78, 7, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:00.975910', '2025-10-21T17:21:00.975917', FALSE, NULL, NULL, NULL, FALSE),
  (79, 6, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.030970', '2025-10-21T17:21:01.030975', FALSE, NULL, NULL, NULL, FALSE),
  (80, 14, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.087144', '2025-10-21T17:21:01.087148', FALSE, NULL, NULL, NULL, FALSE),
  (81, 5, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.141337', '2025-10-21T17:21:01.141341', FALSE, NULL, NULL, NULL, FALSE),
  (82, 4, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.194675', '2025-10-21T17:21:01.194679', FALSE, NULL, NULL, NULL, FALSE),
  (83, 13, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.249157', '2025-10-21T17:21:01.249161', FALSE, NULL, NULL, NULL, FALSE),
  (84, 2, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.304998', '2025-10-21T17:21:01.305002', FALSE, NULL, NULL, NULL, FALSE),
  (85, 3, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.358650', '2025-10-21T17:21:01.358653', FALSE, NULL, NULL, NULL, FALSE),
  (86, 10, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.416518', '2025-10-21T17:21:01.416523', FALSE, NULL, NULL, NULL, FALSE),
  (87, 12, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.469843', '2025-10-21T17:21:01.469846', FALSE, NULL, NULL, NULL, FALSE),
  (88, 11, '2025-10-17', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:01.524351', '2025-10-21T17:21:01.524356', FALSE, NULL, NULL, NULL, FALSE),
  (89, 80, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:25.780521', '2025-10-21T17:21:25.780527', FALSE, NULL, NULL, NULL, FALSE),
  (90, 7, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:25.840685', '2025-10-21T17:21:25.840690', FALSE, NULL, NULL, NULL, FALSE),
  (91, 6, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:25.898475', '2025-10-21T17:21:25.898481', FALSE, NULL, NULL, NULL, FALSE),
  (92, 14, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:25.956684', '2025-10-21T17:21:25.956690', FALSE, NULL, NULL, NULL, FALSE),
  (93, 5, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:26.013756', '2025-10-21T17:21:26.013762', FALSE, NULL, NULL, NULL, FALSE),
  (94, 4, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:26.068138', '2025-10-21T17:21:26.068144', FALSE, NULL, NULL, NULL, FALSE),
  (95, 13, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:26.123772', '2025-10-21T17:21:26.123777', FALSE, NULL, NULL, NULL, FALSE),
  (96, 2, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:26.179428', '2025-10-21T17:21:26.179433', FALSE, NULL, NULL, NULL, FALSE),
  (97, 3, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:26.242337', '2025-10-21T17:21:26.242342', FALSE, NULL, NULL, NULL, FALSE),
  (98, 10, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:26.320836', '2025-10-21T17:21:26.320841', FALSE, NULL, NULL, NULL, FALSE),
  (99, 12, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:26.402840', '2025-10-21T17:21:26.402844', FALSE, NULL, NULL, NULL, FALSE),
  (100, 11, '2025-10-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-21T17:21:26.479994', '2025-10-21T17:21:26.479999', FALSE, NULL, NULL, NULL, FALSE),
  (101, 80, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:02.530701', '2025-10-21T17:46:33.198428', FALSE, NULL, NULL, NULL, FALSE),
  (102, 7, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:02.586139', '2025-10-21T17:46:33.544658', FALSE, NULL, NULL, NULL, FALSE),
  (103, 6, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:02.640322', '2025-10-21T17:46:33.489973', FALSE, NULL, NULL, NULL, FALSE),
  (104, 14, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:02.694211', '2025-10-21T17:46:33.828175', FALSE, NULL, NULL, NULL, FALSE),
  (105, 5, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:02.746013', '2025-10-21T17:46:33.436415', FALSE, NULL, NULL, NULL, FALSE),
  (106, 4, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:02.796849', '2025-10-21T17:46:33.379463', FALSE, NULL, NULL, NULL, FALSE),
  (107, 13, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:02.876708', '2025-10-21T17:46:33.665629', FALSE, NULL, NULL, NULL, FALSE),
  (108, 2, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:02.947746', '2025-10-21T17:46:33.260001', FALSE, NULL, NULL, NULL, FALSE),
  (109, 3, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:03.000541', '2025-10-21T17:46:33.325554', FALSE, NULL, NULL, NULL, FALSE),
  (110, 10, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:03.051601', '2025-10-21T17:46:33.719523', FALSE, NULL, NULL, NULL, FALSE),
  (111, 12, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:03.102031', '2025-10-21T17:46:33.600544', FALSE, NULL, NULL, NULL, FALSE),
  (112, 11, '2025-07-01', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-21T17:45:03.156082', '2025-10-21T17:46:33.775108', FALSE, NULL, NULL, NULL, FALSE),
  (113, 80, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:37.576554', '2025-10-22T00:51:37.576561', FALSE, NULL, NULL, NULL, FALSE),
  (114, 7, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:38.150977', '2025-10-22T00:51:38.151001', FALSE, NULL, NULL, NULL, FALSE),
  (115, 6, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:38.712593', '2025-10-22T00:51:38.712606', FALSE, NULL, NULL, NULL, FALSE),
  (116, 14, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:39.332250', '2025-10-22T00:51:39.332267', FALSE, NULL, NULL, NULL, FALSE),
  (117, 5, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:39.940330', '2025-10-22T00:51:39.940585', FALSE, NULL, NULL, NULL, FALSE),
  (118, 4, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:40.513578', '2025-10-22T00:51:40.513593', FALSE, NULL, NULL, NULL, FALSE),
  (119, 13, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:41.089343', '2025-10-22T00:51:41.089406', FALSE, NULL, NULL, NULL, FALSE),
  (120, 2, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:41.737741', '2025-10-22T00:51:41.737793', FALSE, NULL, NULL, NULL, FALSE),
  (121, 3, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:42.388825', '2025-10-22T00:51:42.388837', FALSE, NULL, NULL, NULL, FALSE),
  (122, 10, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:42.955452', '2025-10-22T00:51:42.955474', FALSE, NULL, NULL, NULL, FALSE),
  (123, 12, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:43.617357', '2025-10-22T00:51:43.617363', FALSE, NULL, NULL, NULL, FALSE),
  (124, 11, '2025-10-22', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T00:51:44.183757', '2025-10-22T00:51:44.183763', FALSE, NULL, NULL, NULL, FALSE),
  (125, 80, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:08.426390', '2025-10-22T01:09:08.426403', FALSE, NULL, NULL, NULL, FALSE),
  (126, 7, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:08.976674', '2025-10-22T01:09:08.976694', FALSE, NULL, NULL, NULL, FALSE),
  (127, 6, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:09.519738', '2025-10-22T01:09:09.519757', FALSE, NULL, NULL, NULL, FALSE),
  (128, 14, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:10.081134', '2025-10-22T01:09:10.081151', FALSE, NULL, NULL, NULL, FALSE),
  (129, 5, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:10.645426', '2025-10-22T01:09:10.645435', FALSE, NULL, NULL, NULL, FALSE),
  (130, 4, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:11.210123', '2025-10-22T01:09:11.210131', FALSE, NULL, NULL, NULL, FALSE),
  (131, 13, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:11.748423', '2025-10-22T01:09:11.748435', FALSE, NULL, NULL, NULL, FALSE),
  (132, 2, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:12.293784', '2025-10-22T01:09:12.293803', FALSE, NULL, NULL, NULL, FALSE),
  (133, 3, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:12.855380', '2025-10-22T01:09:12.855392', FALSE, NULL, NULL, NULL, FALSE),
  (134, 10, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:13.421999', '2025-10-22T01:09:13.422011', FALSE, NULL, NULL, NULL, FALSE),
  (135, 12, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:13.973378', '2025-10-22T01:09:13.973392', FALSE, NULL, NULL, NULL, FALSE),
  (136, 11, '2025-10-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:09:14.538648', '2025-10-22T01:09:14.538668', FALSE, NULL, NULL, NULL, FALSE),
  (137, 80, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:17.551673', '2025-10-22T01:10:17.551685', FALSE, NULL, NULL, NULL, FALSE),
  (138, 7, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:18.085110', '2025-10-22T01:10:18.085118', FALSE, NULL, NULL, NULL, FALSE),
  (139, 6, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:18.618954', '2025-10-22T01:10:18.618967', FALSE, NULL, NULL, NULL, FALSE),
  (140, 14, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:19.174542', '2025-10-22T01:10:19.174565', FALSE, NULL, NULL, NULL, FALSE),
  (141, 5, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:19.738751', '2025-10-22T01:10:19.738772', FALSE, NULL, NULL, NULL, FALSE),
  (142, 4, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:20.263047', '2025-10-22T01:10:20.263054', FALSE, NULL, NULL, NULL, FALSE),
  (143, 13, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:20.793878', '2025-10-22T01:10:20.793895', FALSE, NULL, NULL, NULL, FALSE),
  (144, 2, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:21.402989', '2025-10-22T01:10:21.402994', FALSE, NULL, NULL, NULL, FALSE),
  (145, 3, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:21.939082', '2025-10-22T01:10:21.939089', FALSE, NULL, NULL, NULL, FALSE),
  (146, 10, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:22.475931', '2025-10-22T01:10:22.475939', FALSE, NULL, NULL, NULL, FALSE),
  (147, 12, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:23.053892', '2025-10-22T01:10:23.053900', FALSE, NULL, NULL, NULL, FALSE),
  (148, 11, '2025-09-07', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:10:23.619740', '2025-10-22T01:10:23.619757', FALSE, NULL, NULL, NULL, FALSE),
  (149, 80, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:01.099552', '2025-10-22T01:11:01.099561', FALSE, NULL, NULL, NULL, FALSE),
  (150, 7, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:01.653627', '2025-10-22T01:11:01.653636', FALSE, NULL, NULL, NULL, FALSE),
  (151, 6, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:02.180874', '2025-10-22T01:11:02.180893', FALSE, NULL, NULL, NULL, FALSE),
  (152, 14, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:02.742597', '2025-10-22T01:11:02.742605', FALSE, NULL, NULL, NULL, FALSE),
  (153, 5, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:03.276370', '2025-10-22T01:11:03.276375', FALSE, NULL, NULL, NULL, FALSE),
  (154, 4, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:03.822143', '2025-10-22T01:11:03.822153', FALSE, NULL, NULL, NULL, FALSE),
  (155, 13, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:04.357234', '2025-10-22T01:11:04.357238', FALSE, NULL, NULL, NULL, FALSE),
  (156, 2, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:04.877072', '2025-10-22T01:11:04.877084', FALSE, NULL, NULL, NULL, FALSE),
  (157, 3, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:05.429211', '2025-10-22T01:11:05.429216', FALSE, NULL, NULL, NULL, FALSE),
  (158, 10, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:05.943444', '2025-10-22T01:11:05.943447', FALSE, NULL, NULL, NULL, FALSE),
  (159, 12, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:06.462180', '2025-10-22T01:11:06.462184', FALSE, NULL, NULL, NULL, FALSE),
  (160, 11, '2025-09-08', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T01:11:06.987841', '2025-10-22T01:11:06.987846', FALSE, NULL, NULL, NULL, FALSE),
  (161, 80, '2025-09-10', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:29.740677', '2025-10-27T13:45:59.501985', FALSE, NULL, NULL, NULL, TRUE),
  (162, 7, '2025-09-10', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:30.272298', '2025-10-27T13:44:02.557477', FALSE, NULL, NULL, NULL, FALSE),
  (163, 6, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:30.817279', '2025-10-22T02:58:14.067811', FALSE, NULL, NULL, NULL, FALSE),
  (164, 14, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:31.351461', '2025-10-22T02:58:16.832101', FALSE, NULL, NULL, NULL, FALSE),
  (165, 5, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:31.885022', '2025-10-22T02:58:13.489666', FALSE, NULL, NULL, NULL, FALSE),
  (166, 4, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:32.463206', '2025-10-22T02:58:12.959685', FALSE, NULL, NULL, NULL, FALSE),
  (167, 13, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:32.998271', '2025-10-22T02:58:15.175428', FALSE, NULL, NULL, NULL, FALSE),
  (168, 2, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:33.613847', '2025-10-22T02:58:11.791539', FALSE, NULL, NULL, NULL, FALSE),
  (169, 3, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:34.165076', '2025-10-22T02:58:12.345598', FALSE, NULL, NULL, NULL, FALSE),
  (170, 10, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:34.734385', '2025-10-22T02:58:15.737919', FALSE, NULL, NULL, NULL, FALSE),
  (171, 12, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:35.329499', '2025-10-22T02:58:14.613709', FALSE, NULL, NULL, NULL, FALSE),
  (172, 11, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:57:35.880939', '2025-10-22T02:58:16.274549', FALSE, NULL, NULL, NULL, FALSE),
  (173, 80, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:14.183931', '2025-10-22T02:59:14.183951', FALSE, NULL, NULL, NULL, FALSE),
  (174, 7, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:14.731458', '2025-10-22T02:59:14.731464', FALSE, NULL, NULL, NULL, FALSE),
  (175, 6, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:15.285631', '2025-10-22T02:59:15.285923', FALSE, NULL, NULL, NULL, FALSE),
  (176, 14, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:15.809126', '2025-10-22T02:59:15.809130', FALSE, NULL, NULL, NULL, FALSE),
  (177, 5, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:16.370065', '2025-10-22T02:59:16.370073', FALSE, NULL, NULL, NULL, FALSE),
  (178, 4, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:16.909114', '2025-10-22T02:59:16.909121', FALSE, NULL, NULL, NULL, FALSE),
  (179, 13, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:17.482607', '2025-10-22T02:59:17.482614', FALSE, NULL, NULL, NULL, FALSE),
  (180, 2, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:18.034926', '2025-10-22T02:59:18.034932', FALSE, NULL, NULL, NULL, FALSE),
  (181, 3, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:18.617408', '2025-10-22T02:59:18.617414', FALSE, NULL, NULL, NULL, FALSE),
  (182, 10, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:19.153803', '2025-10-22T02:59:19.153808', FALSE, NULL, NULL, NULL, FALSE),
  (183, 12, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:19.707766', '2025-10-22T02:59:19.707772', FALSE, NULL, NULL, NULL, FALSE),
  (184, 11, '2025-09-12', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-22T02:59:20.251277', '2025-10-22T02:59:20.251283', FALSE, NULL, NULL, NULL, FALSE),
  (185, 80, '2025-07-03', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.418324', '2025-10-22T02:39:50.402912', FALSE, NULL, NULL, NULL, FALSE),
  (186, 7, '2025-07-03', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.476406', '2025-10-22T02:39:50.459404', FALSE, NULL, NULL, NULL, FALSE),
  (187, 6, '2025-07-03', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.533816', '2025-10-22T02:40:26.626816', FALSE, NULL, NULL, NULL, FALSE),
  (188, 14, '2025-07-03', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.595860', '2025-10-22T02:40:54.089642', FALSE, NULL, NULL, NULL, FALSE),
  (189, 5, '2025-07-03', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.657254', '2025-10-22T02:39:50.686636', FALSE, NULL, NULL, NULL, FALSE),
  (190, 4, '2025-07-03', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.714321', '2025-10-22T02:39:50.629371', FALSE, NULL, NULL, NULL, FALSE),
  (191, 13, '2025-07-03', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.771909', '2025-10-22T02:39:50.857232', FALSE, NULL, NULL, NULL, FALSE),
  (192, 2, '2025-07-03', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.831026', '2025-10-22T02:39:50.516582', FALSE, NULL, NULL, NULL, FALSE),
  (193, 3, '2025-07-03', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.891893', '2025-10-22T02:39:50.573407', FALSE, NULL, NULL, NULL, FALSE),
  (194, 10, '2025-07-03', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:53.949835', '2025-10-22T02:39:50.912962', FALSE, NULL, NULL, NULL, FALSE),
  (195, 12, '2025-07-03', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:54.009141', '2025-10-22T02:39:50.799778', FALSE, NULL, NULL, NULL, FALSE),
  (196, 11, '2025-07-03', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-22T02:38:54.066089', '2025-10-22T02:39:50.969539', FALSE, NULL, NULL, NULL, FALSE),
  (197, 80, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:30.513793', '2025-10-23T02:06:30.513797', FALSE, NULL, NULL, NULL, FALSE),
  (198, 7, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:30.567508', '2025-10-23T02:06:30.567513', FALSE, NULL, NULL, NULL, FALSE),
  (199, 6, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:30.625254', '2025-10-23T02:06:30.625258', FALSE, NULL, NULL, NULL, FALSE),
  (200, 14, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:30.680662', '2025-10-23T02:06:30.680666', FALSE, NULL, NULL, NULL, FALSE),
  (201, 5, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:30.740247', '2025-10-23T02:06:30.740251', FALSE, NULL, NULL, NULL, FALSE),
  (202, 4, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:30.795778', '2025-10-23T02:06:30.795783', FALSE, NULL, NULL, NULL, FALSE),
  (203, 13, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:30.857520', '2025-10-23T02:06:30.857525', FALSE, NULL, NULL, NULL, FALSE),
  (204, 2, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:30.910350', '2025-10-23T02:06:30.910355', FALSE, NULL, NULL, NULL, FALSE),
  (205, 83, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:30.963022', '2025-10-23T02:06:30.963026', FALSE, NULL, NULL, NULL, FALSE),
  (206, 84, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:31.015948', '2025-10-23T02:06:31.015953', FALSE, NULL, NULL, NULL, FALSE),
  (207, 3, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:31.070819', '2025-10-23T02:06:31.070823', FALSE, NULL, NULL, NULL, FALSE),
  (208, 10, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:31.123920', '2025-10-23T02:06:31.123924', FALSE, NULL, NULL, NULL, FALSE),
  (209, 12, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:31.176338', '2025-10-23T02:06:31.176342', FALSE, NULL, NULL, NULL, FALSE),
  (210, 11, '2025-10-23', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-23T02:06:31.228798', '2025-10-23T02:06:31.228802', FALSE, NULL, NULL, NULL, FALSE),
  (211, 80, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.256656', '2025-10-25T00:09:10.256660', FALSE, NULL, NULL, NULL, FALSE),
  (212, 7, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.310071', '2025-10-25T00:09:10.310078', FALSE, NULL, NULL, NULL, FALSE),
  (213, 6, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.362514', '2025-10-25T00:09:10.362518', FALSE, NULL, NULL, NULL, FALSE),
  (214, 14, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.416453', '2025-10-25T00:09:10.416457', FALSE, NULL, NULL, NULL, FALSE),
  (215, 5, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.469491', '2025-10-25T00:09:10.469497', FALSE, NULL, NULL, NULL, FALSE),
  (216, 4, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.522042', '2025-10-25T00:09:10.522046', FALSE, NULL, NULL, NULL, FALSE),
  (217, 13, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.576362', '2025-10-25T00:09:10.576367', FALSE, NULL, NULL, NULL, FALSE),
  (218, 2, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.628713', '2025-10-25T00:09:10.628717', FALSE, NULL, NULL, NULL, FALSE),
  (219, 83, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.682607', '2025-10-25T00:09:10.682612', FALSE, NULL, NULL, NULL, FALSE),
  (220, 84, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.734477', '2025-10-25T00:09:10.734480', FALSE, NULL, NULL, NULL, FALSE),
  (221, 3, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.790249', '2025-10-25T00:09:10.790253', FALSE, NULL, NULL, NULL, FALSE),
  (222, 10, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.844378', '2025-10-25T00:09:10.844383', FALSE, NULL, NULL, NULL, FALSE),
  (223, 12, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.896922', '2025-10-25T00:09:10.896926', FALSE, NULL, NULL, NULL, FALSE),
  (224, 11, '2025-10-25', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-25T00:09:10.950530', '2025-10-25T00:09:10.950534', FALSE, NULL, NULL, NULL, FALSE),
  (225, 80, '2025-10-27', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:38.897092', '2025-10-27T13:21:56.571748', FALSE, NULL, NULL, NULL, FALSE),
  (226, 7, '2025-10-27', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:38.950020', '2025-10-27T12:56:30.665805', FALSE, NULL, NULL, NULL, FALSE),
  (227, 6, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.000442', '2025-10-27T12:55:04.114724', FALSE, NULL, NULL, NULL, FALSE),
  (228, 14, '2025-10-27', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Leave', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.056202', '2025-10-27T12:59:38.184494', FALSE, NULL, NULL, NULL, FALSE),
  (229, 5, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.107510', '2025-10-27T12:55:03.612026', FALSE, NULL, NULL, NULL, FALSE),
  (230, 4, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.158363', '2025-10-27T12:55:03.109134', FALSE, NULL, NULL, NULL, FALSE),
  (231, 13, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.209147', '2025-10-27T12:55:05.135053', FALSE, NULL, NULL, NULL, FALSE),
  (232, 2, '2025-10-27', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.260583', '2025-10-27T13:09:51.791795', FALSE, NULL, NULL, NULL, FALSE),
  (233, 83, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.311368', '2025-10-27T12:55:01.584646', FALSE, NULL, NULL, NULL, FALSE),
  (234, 84, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.364079', '2025-10-27T12:55:07.157507', FALSE, NULL, NULL, NULL, FALSE),
  (235, 3, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.415957', '2025-10-27T12:55:02.599285', FALSE, NULL, NULL, NULL, FALSE),
  (236, 10, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.467336', '2025-10-27T12:55:05.645777', FALSE, NULL, NULL, NULL, FALSE),
  (237, 12, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.520915', '2025-10-27T12:55:04.627016', FALSE, NULL, NULL, NULL, FALSE),
  (238, 11, '2025-10-27', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T07:10:39.570960', '2025-10-27T12:55:06.150022', FALSE, NULL, NULL, NULL, FALSE),
  (239, 80, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:11.589289', '2025-10-27T12:53:11.589289', FALSE, NULL, NULL, NULL, FALSE),
  (240, 7, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:12.097236', '2025-10-27T12:53:12.097236', FALSE, NULL, NULL, NULL, FALSE),
  (241, 6, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:12.607233', '2025-10-27T12:53:12.607233', FALSE, NULL, NULL, NULL, FALSE),
  (242, 14, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:13.119641', '2025-10-27T12:53:13.119641', FALSE, NULL, NULL, NULL, FALSE),
  (243, 5, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:13.631045', '2025-10-27T12:53:13.631045', FALSE, NULL, NULL, NULL, FALSE),
  (244, 4, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:14.138855', '2025-10-27T12:53:14.138855', FALSE, NULL, NULL, NULL, FALSE),
  (245, 13, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:14.648066', '2025-10-27T12:53:14.648066', FALSE, NULL, NULL, NULL, FALSE),
  (246, 2, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:15.161050', '2025-10-27T12:53:15.161050', FALSE, NULL, NULL, NULL, FALSE),
  (247, 83, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:15.667800', '2025-10-27T12:53:15.667800', FALSE, NULL, NULL, NULL, FALSE),
  (248, 84, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:16.180214', '2025-10-27T12:53:16.180214', FALSE, NULL, NULL, NULL, FALSE),
  (249, 3, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:16.693347', '2025-10-27T12:53:16.693347', FALSE, NULL, NULL, NULL, FALSE),
  (250, 10, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:17.205021', '2025-10-27T12:53:17.205021', FALSE, NULL, NULL, NULL, FALSE),
  (251, 12, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:17.706938', '2025-10-27T12:53:17.706938', FALSE, NULL, NULL, NULL, FALSE),
  (252, 11, '2025-10-26', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:53:18.218674', '2025-10-27T12:53:18.218674', FALSE, NULL, NULL, NULL, FALSE),
  (253, 80, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:14.927802', '2025-10-27T12:58:14.927802', FALSE, NULL, NULL, NULL, FALSE),
  (254, 7, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:15.424802', '2025-10-27T12:58:15.424802', FALSE, NULL, NULL, NULL, FALSE),
  (255, 6, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:15.994719', '2025-10-27T12:58:15.994719', FALSE, NULL, NULL, NULL, FALSE),
  (256, 14, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:16.488503', '2025-10-27T12:58:16.488503', FALSE, NULL, NULL, NULL, FALSE),
  (257, 5, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:16.977966', '2025-10-27T12:58:16.977966', FALSE, NULL, NULL, NULL, FALSE),
  (258, 4, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:17.485502', '2025-10-27T12:58:17.485502', FALSE, NULL, NULL, NULL, FALSE),
  (259, 13, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:17.987274', '2025-10-27T12:58:17.987274', FALSE, NULL, NULL, NULL, FALSE),
  (260, 2, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:18.485741', '2025-10-27T12:58:18.485741', FALSE, NULL, NULL, NULL, FALSE),
  (261, 83, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:18.981512', '2025-10-27T12:58:18.981512', FALSE, NULL, NULL, NULL, FALSE),
  (262, 84, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:19.472080', '2025-10-27T12:58:19.472080', FALSE, NULL, NULL, NULL, FALSE),
  (263, 3, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:19.970537', '2025-10-27T12:58:19.970537', FALSE, NULL, NULL, NULL, FALSE),
  (264, 10, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:20.456680', '2025-10-27T12:58:20.456680', FALSE, NULL, NULL, NULL, FALSE),
  (265, 12, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:20.954041', '2025-10-27T12:58:20.954041', FALSE, NULL, NULL, NULL, FALSE),
  (266, 11, '2025-10-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T12:58:21.435711', '2025-10-27T12:58:21.435711', FALSE, NULL, NULL, NULL, FALSE),
  (267, 80, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.212094', '2025-10-27T07:32:08.212100', FALSE, NULL, NULL, NULL, FALSE),
  (268, 7, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.267935', '2025-10-27T07:32:08.267940', FALSE, NULL, NULL, NULL, FALSE),
  (269, 6, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.322684', '2025-10-27T07:32:08.322688', FALSE, NULL, NULL, NULL, FALSE),
  (270, 14, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.376992', '2025-10-27T07:32:08.376996', FALSE, NULL, NULL, NULL, FALSE),
  (271, 5, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.430987', '2025-10-27T07:32:08.430990', FALSE, NULL, NULL, NULL, FALSE),
  (272, 4, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.483875', '2025-10-27T07:32:08.483880', FALSE, NULL, NULL, NULL, FALSE),
  (273, 13, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.536944', '2025-10-27T07:32:08.536948', FALSE, NULL, NULL, NULL, FALSE),
  (274, 2, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.590116', '2025-10-27T07:32:08.590121', FALSE, NULL, NULL, NULL, FALSE),
  (275, 83, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.643510', '2025-10-27T07:32:08.643514', FALSE, NULL, NULL, NULL, FALSE),
  (276, 84, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.696665', '2025-10-27T07:32:08.696669', FALSE, NULL, NULL, NULL, FALSE),
  (277, 3, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.749503', '2025-10-27T07:32:08.749508', FALSE, NULL, NULL, NULL, FALSE),
  (278, 10, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.803781', '2025-10-27T07:32:08.803786', FALSE, NULL, NULL, NULL, FALSE),
  (279, 12, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.857709', '2025-10-27T07:32:08.857713', FALSE, NULL, NULL, NULL, FALSE),
  (280, 11, '2025-06-15', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T07:32:08.911328', '2025-10-27T07:32:08.911332', FALSE, NULL, NULL, NULL, FALSE),
  (281, 83, '2025-10-16', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T13:00:50.159471', '2025-10-27T13:00:50.159471', FALSE, NULL, NULL, NULL, FALSE),
  (282, 84, '2025-10-16', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Pending', 'Auto-generated attendance record', NULL, NULL, '2025-10-27T13:00:50.683672', '2025-10-27T13:00:50.683672', FALSE, NULL, NULL, NULL, FALSE),
  (283, 80, '2025-09-24', NULL, NULL, NULL, NULL, '0.00', '0.00', '0.00', 'Absent', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:36.325838', '2025-10-27T13:26:42.790443', FALSE, NULL, NULL, NULL, FALSE),
  (284, 7, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:36.833518', '2025-10-27T13:26:43.270369', FALSE, NULL, NULL, NULL, FALSE),
  (285, 6, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:37.451527', '2025-10-27T13:26:46.408965', FALSE, NULL, NULL, NULL, FALSE),
  (286, 14, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:38.056930', '2025-10-27T13:26:49.252874', FALSE, NULL, NULL, NULL, FALSE),
  (287, 5, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:38.677177', '2025-10-27T13:26:45.921791', FALSE, NULL, NULL, NULL, FALSE),
  (288, 4, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:39.173026', '2025-10-27T13:26:45.447659', FALSE, NULL, NULL, NULL, FALSE),
  (289, 13, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:39.810183', '2025-10-27T13:26:47.389036', FALSE, NULL, NULL, NULL, FALSE),
  (290, 2, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:40.420385', '2025-10-27T13:26:44.359328', FALSE, NULL, NULL, NULL, FALSE),
  (291, 83, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:40.973246', '2025-10-27T13:26:43.843535', FALSE, NULL, NULL, NULL, FALSE),
  (292, 84, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:41.546597', '2025-10-27T13:26:49.808187', FALSE, NULL, NULL, NULL, FALSE),
  (293, 3, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:42.162582', '2025-10-27T13:26:44.855809', FALSE, NULL, NULL, NULL, FALSE),
  (294, 10, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:42.773841', '2025-10-27T13:26:47.960635', FALSE, NULL, NULL, NULL, FALSE),
  (295, 12, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:43.391960', '2025-10-27T13:26:46.904208', FALSE, NULL, NULL, NULL, FALSE),
  (296, 11, '2025-09-24', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:25:43.900229', '2025-10-27T13:26:48.598013', FALSE, NULL, NULL, NULL, FALSE),
  (297, 83, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:42:46.693021', '2025-10-27T13:44:03.170392', FALSE, NULL, NULL, NULL, FALSE),
  (298, 84, '2025-09-10', NULL, NULL, NULL, NULL, '8.00', '0.00', '8.00', 'Present', 'Updated by Team Manager', NULL, NULL, '2025-10-27T13:42:47.214602', '2025-10-27T13:44:06.854870', FALSE, NULL, NULL, NULL, FALSE);



-- ============================================
-- TABLE: HRM_LEAVE (9 rows)
-- ============================================
INSERT INTO hrm_leave (id, employee_id, leave_type, start_date, end_date, days_requested, reason, status, requested_by, approved_by, approved_at, rejection_reason, created_at, updated_at) VALUES
  (1, 5, 'Annual Leave', '2025-10-08', '2025-10-09', 2, '', 'Pending', NULL, NULL, NULL, NULL, '2025-10-06T10:46:21.000436', '2025-10-06T10:46:21.000440'),
  (2, 13, 'Medical Leave', '2025-10-14', '2025-10-14', 1, 'Medical leave', 'Pending', 12, NULL, NULL, NULL, '2025-10-12T13:13:01.112494', '2025-10-12T13:13:01.112498'),
  (3, 14, 'Annual Leave', '2025-10-11', '2025-10-12', 2, '', 'Pending', 13, NULL, NULL, NULL, '2025-10-12T13:27:35.674302', '2025-10-12T13:27:35.674306'),
  (4, 13, 'Annual Leave', '2025-10-01', '2025-10-04', 4, '', 'Pending', 12, NULL, NULL, NULL, '2025-10-12T13:42:22.390614', '2025-10-12T13:42:22.390618'),
  (5, 12, 'Medical Leave', '2025-10-13', '2025-10-13', 1, '', 'Pending', 11, NULL, NULL, NULL, '2025-10-14T03:00:34.371290', '2025-10-14T03:00:34.371294'),
  (6, 13, 'Annual Leave', '2025-10-13', '2025-10-13', 1, '', 'Pending', 12, NULL, NULL, NULL, '2025-10-14T03:02:00.834682', '2025-10-14T03:02:00.834686'),
  (7, 11, 'Casual Leave', '2025-10-17', '2025-10-17', 1, 'test', 'Pending', 10, NULL, NULL, NULL, '2025-10-15T11:47:16.879908', '2025-10-15T11:47:16.879912'),
  (8, 11, 'Annual Leave', '2025-10-17', '2025-10-17', 1, '', 'Pending', 10, NULL, NULL, NULL, '2025-10-15T13:53:54.059109', '2025-10-15T13:53:54.059114'),
  (9, 13, 'Casual Leave', '2025-10-17', '2025-10-17', 1, '', 'Pending', 12, NULL, NULL, NULL, '2025-10-15T16:35:10.013759', '2025-10-15T16:35:10.013765');


-- Table 'hrm_claim' is empty


-- Table 'hrm_appraisal' is empty



-- ============================================
-- TABLE: HRM_ROLES (8 rows)
-- ============================================
INSERT INTO hrm_roles (id, name, description, is_active, created_at, updated_at) VALUES
  (1, 'Software Engineer', 'Develops and maintains software applications', TRUE, '2025-10-16T07:55:33.573098', '2025-10-16T07:55:33.573104'),
  (2, 'Senior Developer', 'Senior software development role with leadership responsibilities', TRUE, '2025-10-16T07:55:33.573107', '2025-10-16T07:55:33.573108'),
  (3, 'Team Lead', 'Leads development teams and manages projects', TRUE, '2025-10-16T07:55:33.573110', '2025-10-16T07:55:33.573111'),
  (4, 'HR Manager', 'Manages human resources operations', TRUE, '2025-10-16T07:55:33.573113', '2025-10-16T07:55:33.573114'),
  (5, 'Sales Executive', 'Responsible for sales activities and client relationships', TRUE, '2025-10-16T07:55:33.573116', '2025-10-16T07:55:33.573117'),
  (6, 'Marketing Specialist', 'Handles marketing campaigns and brand management', TRUE, '2025-10-16T07:55:33.573119', '2025-10-16T07:55:33.573120'),
  (7, 'Accountant', 'Manages financial records and accounting operations', TRUE, '2025-10-16T07:55:33.573122', '2025-10-16T07:55:33.573123'),
  (8, 'Operations Manager', 'Oversees daily business operations', TRUE, '2025-10-16T07:55:33.573125', '2025-10-16T07:55:33.573126');



-- ============================================
-- TABLE: HRM_DEPARTMENTS (6 rows)
-- ============================================
INSERT INTO hrm_departments (id, name, description, manager_id, is_active, created_at, updated_at) VALUES
  (1, 'Information Technology', 'Software development and IT services', NULL, TRUE, '2025-09-30T17:29:41.011783', '2025-09-30T17:29:41.011783'),
  (2, 'Human Resources', 'Employee relations and HR operations', NULL, TRUE, '2025-09-30T17:29:41.011783', '2025-09-30T17:29:41.011783'),
  (3, 'Sales & Marketing', 'Sales and marketing activities', NULL, TRUE, '2025-09-30T17:29:41.011783', '2025-09-30T17:29:41.011783'),
  (4, 'Finance & Accounting', 'Financial planning and accounting', NULL, TRUE, '2025-09-30T17:29:41.011783', '2025-09-30T17:29:41.011783'),
  (5, 'Operations', 'Business operations and logistics', NULL, TRUE, '2025-09-30T17:29:41.011783', '2025-09-30T17:29:41.011783'),
  (6, 'Administration', 'General administration and support', NULL, TRUE, '2025-09-30T17:29:41.011783', '2025-09-30T17:29:41.011783');


-- Table 'hrm_compliance_report' is empty



-- ============================================
-- TABLE: HRM_TENANT_PAYMENT_CONFIG (1 rows)
-- ============================================
INSERT INTO hrm_tenant_payment_config (id, tenant_id, payment_type, implementation_charges, monthly_charges, other_charges, frequency, created_by, created_at, modified_by, modified_at) VALUES
  (1, 'a4c3e2ed-cfac-47ca-8a51-0a5becb1a12d', 'Fixed', '500.00', '150.00', '0.00', 'Half-Yearly', 'admin@noltrion.com', '2025-10-08T15:14:52.777749+00:00', NULL, NULL);



-- ============================================
-- TABLE: HRM_ROLE_ACCESS_CONTROL (47 rows)
-- ============================================
INSERT INTO hrm_role_access_control (id, module_name, menu_name, sub_menu_name, super_admin_access, tenant_admin_access, hr_manager_access, employee_access, created_at, updated_at, created_by, updated_by) VALUES
  (1, 'Payroll', 'Payroll Management', 'Payroll List', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633895', '2025-10-18T02:13:53.633911', 'system', NULL),
  (2, 'Payroll', 'Payroll Management', 'Payroll Generation', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633917', '2025-10-18T02:13:53.633921', 'system', NULL),
  (3, 'Payroll', 'Payroll Management', 'Payroll Approval', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633925', '2025-10-18T02:13:53.633929', 'system', NULL),
  (4, 'Payroll', 'Payroll Management', 'Payroll History', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633933', '2025-10-18T02:13:53.633937', 'system', NULL),
  (5, 'Payroll', 'Payslip Management', 'View Payslips', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633941', '2025-10-18T02:13:53.633944', 'system', NULL),
  (6, 'Payroll', 'Payslip Management', 'Download Payslips', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633948', '2025-10-18T02:13:53.633952', 'system', NULL),
  (7, 'Payroll', 'Payslip Management', 'Print Payslips', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633956', '2025-10-18T02:13:53.633959', 'system', NULL),
  (8, 'Payroll', 'Payroll Reports', 'Salary Reports', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633963', '2025-10-18T02:13:53.633967', 'system', NULL),
  (9, 'Payroll', 'Payroll Reports', 'Tax Reports', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633971', '2025-10-18T02:13:53.633974', 'system', NULL),
  (10, 'Payroll', 'Payroll Reports', 'Deduction Reports', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633978', '2025-10-18T02:13:53.633981', 'system', NULL),
  (11, 'Attendance', 'Attendance Management', 'Mark Attendance', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633985', '2025-10-18T02:13:53.633989', 'system', NULL),
  (12, 'Attendance', 'Attendance Management', 'Attendance List', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.633993', '2025-10-18T02:13:53.633996', 'system', NULL),
  (13, 'Attendance', 'Attendance Management', 'Attendance Reports', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634000', '2025-10-18T02:13:53.634004', 'system', NULL),
  (14, 'Attendance', 'Attendance Management', 'Bulk Upload', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634008', '2025-10-18T02:13:53.634011', 'system', NULL),
  (15, 'Attendance', 'Leave Management', 'Apply Leave', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634015', '2025-10-18T02:13:53.634019', 'system', NULL),
  (16, 'Attendance', 'Leave Management', 'Leave Approval', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634023', '2025-10-18T02:13:53.634026', 'system', NULL),
  (17, 'Attendance', 'Leave Management', 'Leave Balance', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634030', '2025-10-18T02:13:53.634033', 'system', NULL),
  (18, 'Attendance', 'Leave Management', 'Leave Reports', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634037', '2025-10-18T02:13:53.634040', 'system', NULL),
  (19, 'Employees', 'Employee Management', 'View Employees', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634044', '2025-10-18T02:13:53.634047', 'system', NULL),
  (20, 'Employees', 'Employee Management', 'Add Employee', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634051', '2025-10-18T02:13:53.634055', 'system', NULL),
  (21, 'Employees', 'Employee Management', 'Edit Employee', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634059', '2025-10-18T02:13:53.634062', 'system', NULL),
  (22, 'Employees', 'Employee Management', 'Employee List', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634066', '2025-10-18T02:13:53.634069', 'system', NULL),
  (23, 'Employees', 'Employee Documents', 'Upload Documents', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634073', '2025-10-18T02:13:53.634077', 'system', NULL),
  (24, 'Employees', 'Employee Documents', 'View Documents', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634081', '2025-10-18T02:13:53.634084', 'system', NULL),
  (25, 'Employees', 'Employee Documents', 'Download Documents', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634088', '2025-10-18T02:13:53.634091', 'system', NULL),
  (26, 'Employees', 'Employee Reports', 'Employee Directory', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634095', '2025-10-18T02:13:53.634098', 'system', NULL),
  (27, 'Employees', 'Employee Reports', 'Employee Summary', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634102', '2025-10-18T02:13:53.634106', 'system', NULL),
  (28, 'Claims', 'Expense Claims', 'Submit Claim', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634110', '2025-10-18T02:13:53.634113', 'system', NULL),
  (29, 'Claims', 'Expense Claims', 'Claim Approval', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634117', '2025-10-18T02:13:53.634120', 'system', NULL),
  (30, 'Claims', 'Expense Claims', 'Claim History', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634124', '2025-10-18T02:13:53.634128', 'system', NULL),
  (31, 'Claims', 'Claim Reports', 'Claim Summary', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634132', '2025-10-18T02:13:53.634135', 'system', NULL),
  (32, 'Claims', 'Claim Reports', 'Claim Analysis', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634139', '2025-10-18T02:13:53.634142', 'system', NULL),
  (33, 'Appraisals', 'Appraisal Management', 'Create Appraisal', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634146', '2025-10-18T02:13:53.634149', 'system', NULL),
  (34, 'Appraisals', 'Appraisal Management', 'View Appraisals', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634153', '2025-10-18T02:13:53.634156', 'system', NULL),
  (35, 'Appraisals', 'Appraisal Management', 'Submit Appraisal', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634160', '2025-10-18T02:13:53.634163', 'system', NULL),
  (36, 'Appraisals', 'Appraisal Reports', 'Appraisal Summary', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634167', '2025-10-18T02:13:53.634170', 'system', NULL),
  (37, 'Appraisals', 'Appraisal Reports', 'Performance Reports', 'Editable', 'Editable', 'View Only', 'View Only', '2025-10-18T02:13:53.634174', '2025-10-18T02:13:53.634178', 'system', NULL),
  (38, 'Admin Settings', 'Access Control Configuration', 'View Access Matrix', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634182', '2025-10-18T02:13:53.634185', 'system', NULL),
  (39, 'Admin Settings', 'Access Control Configuration', 'Edit Access Matrix', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634189', '2025-10-18T02:13:53.634192', 'system', NULL),
  (40, 'Admin Settings', 'Access Control Configuration', 'Export Matrix', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634196', '2025-10-18T02:13:53.634199', 'system', NULL),
  (41, 'Admin Settings', 'Access Control Configuration', 'Import Matrix', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634203', '2025-10-18T02:13:53.634207', 'system', NULL),
  (42, 'Admin Settings', 'User Role Mapping', 'Map Roles', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634211', '2025-10-18T02:13:53.634214', 'system', NULL),
  (43, 'Admin Settings', 'User Role Mapping', 'Manage User Roles', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634218', '2025-10-18T02:13:53.634221', 'system', NULL),
  (44, 'Admin Settings', 'User Role Mapping', 'Manage Company Access', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634225', '2025-10-18T02:13:53.634228', 'system', NULL),
  (45, 'Admin Settings', 'Master Data', 'Manage Roles', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634232', '2025-10-18T02:13:53.634236', 'system', NULL),
  (46, 'Admin Settings', 'Master Data', 'Manage Departments', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634240', '2025-10-18T02:13:53.634243', 'system', NULL),
  (47, 'Admin Settings', 'Master Data', 'Manage Designations', 'Editable', 'Hidden', 'Hidden', 'Hidden', '2025-10-18T02:13:53.634247', '2025-10-18T02:13:53.634251', 'system', NULL);


-- Table 'hrm_user_role_mapping' is empty


-- Table 'hrm_tenant_documents' is empty

