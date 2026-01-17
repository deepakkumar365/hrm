# AWS S3 Integration Test Plan

## 1. Environment Configuration Verification
**Objective:** Ensure the application environment is correctly configured to communicate with AWS S3.

| Step | Action | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- |
| 1.1 | Check `.env` file for `AWS_ACCESS_KEY_ID`. | Key exists and has a value. | |
| 1.2 | Check `.env` file for `AWS_SECRET_ACCESS_KEY`. | Key exists and has a value. | |
| 1.3 | Check `.env` file for `AWS_REGION`. | Key exists (e.g., `ap-southeast-1`). | |
| 1.4 | Check `.env` file for `AWS_S3_BUCKET_NAME`. | Key exists and matches the target bucket. | |
| 1.5 | Verify `S3Service` initialization. | `S3Service` class initializes `boto3.client` without errors. | |

## 2. Connectivity & Basic Operations (Unit Testing)
**Objective:** Verify that the `S3Service` can perform basic CRUD operations on the S3 bucket.
*These tests can be run via a python shell or a dedicated test script.*

| Step | Action | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- |
| 2.1 | **Upload Test**: Call `S3Service().upload_file` with a dummy text file. | Method returns `True`. File appears in S3 bucket. | |
| 2.2 | **Presigned URL Test**: Call `S3Service().generate_presigned_url` for the uploaded file. | Method returns a valid URL starting with `https://`. Accessing URL downloads the file. | |
| 2.3 | **Delete Test**: Call `S3Service().delete_file` for the uploaded file. | Method returns `True`. File is removed from S3 bucket. | |
| 2.4 | **Error Handling**: Attempt to download/delete a non-existent file. | Service handles `ClientError` gracefully, logs error, returns `False` or `None`. | |

## 3. `FileService` Integration Testing
**Objective:** Verify that `FileService` correctly manages the file lifecycle (Database + S3) and enforces path structures.

| Step | Action | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- |
| 3.1 | **Upload Profile Picture**: Upload a new profile picture for an employee via `FileService.upload_file`. | correct path: `tenants/{id}/companies/{id}/employees/{id}/profile_pictures/...`. DB Record created in `hrm_file_storage`. | |
| 3.2 | **Upload Tenant Logo**: Upload a standard tenant logo. | correct path: `tenants/{id}/global/payslip_logos/...`. DB Record created. | |
| 3.3 | **Retrieve URL**: Call `FileService.get_file_url(file_id)`. | Returns a valid presigned S3 URL. | |

## 4. Application Feature Verification (End-to-End)
**Objective:** Verify the user-facing features impacted by S3 integration.

### 4.1 Employee Profile Picture
1.  Navigate to **Employee Edit** page.
2.  Upload a new profile picture.
3.  Save changes.
4.  **Verify:** The new image displays correctly on the profile page.
5.  **Verify:** The image URL in the browser inspector points to S3 (or a signed URL).

### 4.2 Attendance Proof Document
1.  Navigate to **Attendance List**.
2.  Click "Regularize" for an absent record.
3.  Upload a proof document (PDF/Image).
4.  Submit request.
5.  **Verify:** Regularization request is created.
6.  **Verify:** Manager can view/download the proof document from the approval screen.

### 4.3 Payslip Logo
1.  Navigate to **Tenant Configuration**.
2.  Upload a new Payslip Logo.
3.  Generate a **Payslip Preview** for an employee.
4.  **Verify:** The new logo appears on the payslip.
5.  **Verify:** The logo renders correctly (no broken image icon).

## 5. Security & Access Control
**Objective:** Ensure files are not publicly accessible without a valid signature.

| Step | Action | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- |
| 5.1 | Access Presigned URL. | File downloads successfully. | |
| 5.2 | Wait for expiration (default 1h) or modify URL signature manually. | Access denied (`403 Forbidden`). | |
| 5.3 | Attempt to access S3 object URL directly (without query params). | Access denied (`403 Forbidden`) - Bucket should not be public. | |
