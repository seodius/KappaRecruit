# ATS API - TODO & Improvement Plan

This document outlines potential improvements and future features for the Headless ATS API. It is intended to serve as a roadmap for ongoing development.

---

## High Priority / Next Steps

### 1. **AI-Powered Resume Parsing**
- **Description:** Implement an AI/ML model to automatically parse uploaded resumes (PDFs) and populate the `UnifiedResume` schema. This is the most critical feature to unlock the full potential of the ATS.
- **Tasks:**
    - [ ] Research and select a suitable NLP library or pre-trained model (e.g., spaCy, GPT-based models, or a specialized service).
    - [ ] Create a new service or background job to handle the parsing process asynchronously.
    - [ ] Update the `create_resume` endpoint to trigger the parsing job upon file upload.
    - [ ] Add a `status` field to the `Resume` model to track the parsing state (e.g., `pending`, `success`, `failed`).

### 2. **Refine Multi-Tenancy Security**
- **Description:** The current multi-tenancy logic relies on string-searching a JSON field (`created_by`), which is not robust. This should be refactored to use a direct foreign key relationship.
- **Tasks:**
    - [ ] Add a `created_by_user_id` foreign key column to the `Candidate` model, linking directly to the `User` model.
    - [ ] Update the `_is_candidate_in_company` and `get_candidate` CRUD functions to use this direct relationship for authorization checks, improving security and performance.

### 3. **Enhance API Documentation**
- **Description:** The auto-generated documentation is good, but it can be improved with more detailed descriptions, examples, and explanations of the multi-tenant security model.
- **Tasks:**
    - [ ] Add detailed `description` and `summary` fields to all API endpoints in `main.py` and `api/*.py`.
    - [ ] Include example request and response bodies using Pydantic's `Field` examples.
    - [ ] Write a dedicated section in the `README.md` explaining how to authenticate and interact with the API as a specific tenant.

---

## Medium Priority / Core Feature Enhancements

### 1. **Advanced Search & Filtering**
- **Description:** Implement advanced search capabilities to allow recruiters to filter candidates and jobs based on specific criteria within the JSON data.
- **Tasks:**
    - [ ] Add query parameters to the `/jobs` and `/candidates` GET endpoints.
    - [ ] Implement logic in the CRUD functions to filter results based on skills, experience level, location, etc.

### 2. **Dashboard & Analytics Endpoints**
- **Description:** Create dedicated API endpoints to provide data for a future analytics dashboard.
- **Tasks:**
    - [ ] Develop endpoints to calculate key recruitment metrics (e.g., time-to-fill, source effectiveness, pipeline conversion rates).
    - [ ] Implement data aggregation queries in the `crud.py` layer to efficiently compute these metrics.

### 3. **Webhooks for Third-Party Integrations**
- **Description:** Add a webhook system to notify external services of key events within the ATS (e.g., new application, status change).
- **Tasks:**
    - [ ] Design a `Webhook` model and API for clients to register webhook URLs.
    - [ ] Implement an event-driven system to trigger outgoing webhook calls for important actions.

---

## Low Priority / Long-Term Improvements

### 1. **Database Migrations with Alembic**
- **Description:** The current setup relies on `Base.metadata.create_all()`, which is not suitable for production. Implementing a proper database migration tool is essential for managing schema changes over time.
- **Tasks:**
    - [ ] Integrate `Alembic` into the project.
    - [ ] Create an initial migration script that reflects the current database schema.

### 2. **Asynchronous Task Queue (Celery/Redis)**
- **Description:** Offload long-running tasks like email notifications, resume parsing, and webhook delivery to a background worker.
- **Tasks:**
    - [ ] Integrate Celery and Redis into the application.
    - [ ] Refactor relevant operations to be handled by asynchronous tasks.

### 3. **User & Role Management API**
- **Description:** Expand the API to allow administrators to manage user roles and permissions programmatically.
- **Tasks:**
    - [ ] Create endpoints for creating, updating, and deleting roles and assigning permissions.
    - [ ] Implement more granular Role-Based Access Control (RBAC) throughout the API.
