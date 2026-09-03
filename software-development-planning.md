# AI Prompt: Software Development Planning and Recommended Phasing

Use the Bored Pile Testing Management Tool project context provided with this prompt as the authoritative business background.

Act as a **senior software architect, product manager, business analyst, UX strategist, security engineer, and DevOps adviser**. Develop a practical and comprehensive Software Development Planning Document for the proposed system.

Do not generate application source code yet. The purpose of this task is to determine **what should be built, why it should be built, how the system should be designed, and in what order it should be developed**.

Do not merely repeat the supplied project context. Analyze it, identify gaps, challenge weak assumptions, and provide justified recommendations.

## Important Instructions

- Treat details explicitly stated in the supplied project context as confirmed facts.
- Clearly label all assumptions, interpretations, and recommendations.
- Do not silently invent missing business rules.
- If information is missing, identify the open question and explain why it affects the plan.
- Continue producing the plan using clearly labeled provisional assumptions instead of stopping after asking questions.
- Prioritize an achievable Minimum Viable Product (MVP), but show how it can evolve into a production-scale platform.
- Explain technical terms in clear language.
- Compare alternatives and trade-offs before giving major recommendations.
- Be realistic about development effort, cost, complexity, team size, security, maintenance, and stakeholder readiness.
- Recommend additional planning areas, system capabilities, risks, or development phases that are not explicitly requested but would materially improve the project.

---

# Required Planning Areas

## 1. Executive Summary

Provide a concise summary of:

- The problem being solved
- The intended users and stakeholders
- The proposed solution
- The recommended MVP
- The recommended technical direction
- The recommended development approach
- The most important risks and decisions

## 2. Project Understanding and Product Vision

- Summarize your understanding of the Bored Pile Testing Management Tool.
- Define the product vision and the value it should provide.
- Identify the current operational problems and inefficiencies it should address.
- Explain the expected benefits for the Contractor, Pile Test Engineers, Geotechnical Engineers, GCR, and other relevant stakeholders.
- Define measurable project objectives.
- Identify assumptions that must be validated through stakeholder interviews or process observation.

## 3. Scope Definition

Divide the proposed scope into:

1. Essential MVP capabilities
2. Recommended Version 1 capabilities after MVP validation
3. Future or optional capabilities
4. Capabilities that should remain out of scope for now

Explain why each capability belongs in its assigned category.

Include likely modules such as:

- User and role management
- Project and contract-package management
- Bored pile records
- W.I.R. submission and attachments
- Digital field data sheets
- PIT, PDA, and CSL testing records
- Raw test-data and report uploads
- Geotechnical evaluation reports
- GCR review and submittal statuses
- Comments, revisions, and resubmissions
- Document control and version history
- SLA and turnaround-time tracking
- Notifications and escalations
- Dashboards and reports
- Audit logs
- Administrative configuration

Recommend any missing module that the project may need.

## 4. Stakeholders, User Roles, and Permissions

- Identify every likely stakeholder and user role.
- Describe each role's responsibilities and goals.
- Create a Role-Based Access Control matrix.
- Recommend who may view, create, edit, upload, submit, review, comment, approve, reject, return, archive, restore, export, and delete each type of record.
- Identify actions that require separation of duties.
- Recommend whether DOTr needs direct system access, reporting access, or no access during the MVP.
- Explain how external users, project-specific access, and multi-organization access should work.

## 5. Functional Requirements

List and organize the functional requirements by module.

For each major requirement, provide:

- Requirement name
- Purpose
- Primary user
- Preconditions
- Inputs
- Main process
- Outputs
- Business rules
- Exceptions and validation rules
- Dependencies
- Priority
- MVP or future classification
- Acceptance criteria

Include requirements for:

- Authentication and account administration
- Project, package, location, and bored pile records
- W.I.R. preparation, attachments, validation, submission, and tracking
- Field data collection using mobile or tablet devices
- PIT, PDA, and CSL test workflows
- Raw test report uploads
- Evaluation report preparation and submission
- GCR review, comments, decisions, and resubmissions
- NONO, NONOC C, NONOC B, and NOR statuses
- SLA clocks, deadlines, pauses, overdue states, and escalations
- Search, filters, dashboards, and exports
- Document versions and revision history
- Notifications
- Audit trails
- Report and PDF generation
- Record archival and recovery

## 6. Non-Functional Requirements

Recommend measurable non-functional requirements for:

- Performance
- Availability
- Reliability
- Scalability
- Data integrity
- Security
- Privacy and confidentiality
- Auditability
- Maintainability
- Extensibility
- Accessibility
- Mobile and tablet usability
- Browser compatibility
- File-upload capacity
- Backup and restoration
- Disaster recovery
- Monitoring and alerting
- Document retention
- Construction-site connectivity limitations
- Possible offline or interrupted-connection behavior

Separate essential MVP requirements from requirements that can be strengthened after the MVP.

## 7. Recommended Technology Stack

Recommend a practical technology stack covering:

- Web frontend
- Mobile or progressive web application approach, if appropriate
- Backend language and framework
- API style
- Database
- File or object storage
- Authentication and authorization
- Background jobs and task queues
- Notifications
- Search
- PDF and report generation
- Caching
- Hosting and cloud infrastructure
- Containerization
- CI/CD
- Monitoring, logging, and error tracking
- Automated testing
- Analytics, if needed

For each major choice:

- State its role in the system.
- Explain why it fits this project.
- Provide at least one alternative.
- Compare development speed, cost, complexity, scalability, maintainability, vendor lock-in, security, ecosystem maturity, and required developer experience.
- State whether it is required for the MVP or recommended for a later phase.

Provide a final technology-stack summary table and select one recommended stack rather than leaving all options unresolved.

## 8. Software Architecture

Recommend whether the MVP should use a modular monolith, microservices, serverless architecture, or another approach.

Include:

- A high-level architecture diagram in Mermaid
- Major components and their responsibilities
- Module boundaries
- Frontend-to-backend communication
- Authentication and authorization flow
- Database access
- File upload, storage, retrieval, and versioning
- Background processing
- Notification delivery
- Report generation
- Audit logging
- Monitoring and observability
- Deployment structure
- Scaling strategy
- Future architecture evolution

Explain why the recommended architecture is appropriate for the MVP and what conditions would justify changing it later.

## 9. Data Architecture and Initial Database Design

- Identify the main entities and relationships.
- Produce an initial Entity-Relationship Diagram in Mermaid.
- Recommend an initial logical database schema.
- Identify important primary keys, foreign keys, indexes, unique constraints, status fields, timestamps, and audit fields.
- Explain the relationship among projects, packages, locations, bored piles, test requirements, W.I.R.s, attachments, field data sheets, raw reports, evaluation reports, reviews, comments, revisions, decisions, SLA events, notifications, and audit logs.
- Explain how files should be stored separately from their metadata.
- Recommend how record history and document versions should be preserved.
- Identify data that must never be permanently overwritten.
- Recommend a migration and data-import strategy for existing paper or spreadsheet records.

## 10. Workflow and State-Machine Design

Translate the business process into explicit system workflows for:

- W.I.R. preparation and submission
- Attachment validation
- Test scheduling and execution
- Field data collection
- Raw test report upload
- Geotechnical evaluation
- GCR review
- Commenting and revision
- Approval or rejection
- Resubmission
- Closure and archival
- SLA tracking and escalation

For each workflow:

- Identify responsible roles.
- Define valid statuses.
- Define allowed status transitions.
- Identify invalid or prohibited actions.
- Define which event starts, pauses, resumes, completes, or breaches an SLA.
- Define required notifications.
- Define required audit-log entries.
- Identify unclear rules that stakeholders must confirm.

Include Mermaid flowcharts or state diagrams where they make the workflow easier to understand.

## 11. User Experience and Interface Planning

- Recommend the information architecture and navigation.
- List the main pages and screens.
- Define dashboards for each major role.
- Recommend the field workflow for mobile and tablet users.
- Explain draft saving, validation, incomplete forms, attachments, and interrupted connections.
- Recommend fast ways to locate a bored pile, W.I.R., field sheet, test report, evaluation, or GCR decision.
- Identify useful filters, status indicators, alerts, and dashboard metrics.
- Consider accessibility and responsive design.
- Recommend whether offline data capture is necessary, optional, or too complex for the MVP.
- Provide low-fidelity page descriptions for the most important MVP screens.

## 12. Document and Records Management

Recommend:

- Document categories
- Naming conventions
- Metadata and tagging
- Folder or virtual-folder organization
- File-type and file-size rules
- Versioning and revision control
- Approval timestamps
- Retention and archival
- Restore and recovery
- Download and sharing permissions
- Watermarking, if appropriate
- Electronic signatures, if appropriate
- Immutable audit history
- Traceability among the bored pile, W.I.R., field data sheet, raw test report, evaluation report, and GCR decision

Explain which controls are essential for the MVP and which may be introduced later.

## 13. Security and Data Protection

- Identify sensitive data and likely threats.
- Recommend authentication and session controls.
- Recommend authorization and project-level access controls.
- Define encryption requirements for data in transit and at rest.
- Recommend safe file-upload controls, file validation, malware scanning, and permission checks.
- Address common web application vulnerabilities.
- Recommend audit-logging requirements.
- Define backup, restoration, disaster-recovery, and retention practices.
- Recommend secrets management.
- Identify whether any Philippine laws, contractual obligations, infrastructure-security rules, or organizational policies require confirmation by legal or compliance specialists.
- Separate MVP security controls from later security enhancements.

## 14. API and Integration Planning

- Recommend REST, GraphQL, or another API style.
- Identify conceptual API resources.
- Explain validation, errors, pagination, filtering, sorting, file uploads, authorization, idempotency, and versioning.
- Recommend possible integrations for email, SMS, enterprise identity, cloud storage, engineering systems, analytics, and document-signing services.
- Distinguish required MVP integrations from optional future integrations.
- Identify integration risks and fallback strategies.

## 15. Testing and Quality Assurance

Develop a testing strategy covering:

- Unit tests
- Integration tests
- API tests
- Database tests
- End-to-end tests
- Workflow and status-transition tests
- Roles and permission tests
- File-upload and document-version tests
- Responsive and device tests
- Accessibility tests
- Performance and load tests
- Security tests
- Backup and restore tests
- User Acceptance Testing

Provide example acceptance criteria and test scenarios for the most critical MVP workflows.

## 16. DevOps, Environments, and Operations

Recommend:

- Local development practices
- Development, testing, staging, and production environments
- Git branching and code review
- CI/CD pipeline
- Database migration and rollback
- Infrastructure configuration
- Environment variables and secrets
- Monitoring, logging, metrics, tracing, and alerts
- Release, rollback, and hotfix procedures
- Incident response
- Support and maintenance ownership
- Data backup verification
- Operational documentation

## 17. Recommended Software Development Phasing

Do not simply follow a generic sequence. Recommend the best phasing strategy for this specific project.

First, compare at least three possible approaches:

1. **Lean prototype-first approach** — prioritize rapid validation with a narrow workflow.
2. **Balanced MVP approach** — establish the technical foundation and deliver an end-to-end usable workflow.
3. **Broader platform-first approach** — build more shared infrastructure and modules before pilot deployment.

For each approach, explain:

- Advantages
- Disadvantages
- Cost and time implications
- Technical and operational risks
- Appropriate team size
- When the approach would be suitable

Then select and justify one recommended approach.

Create a detailed recommended phase plan. You may improve, reorganize, split, combine, remove, or add phases as needed. Consider the following starting structure:

### Phase 0: Discovery and Domain Validation

- Stakeholder interviews
- Existing workflow observation
- Document and form inventory
- Terminology validation
- Status and SLA rule confirmation
- Data ownership and security confirmation
- MVP success criteria

### Phase 1: Product and UX Definition

- User journeys
- Process maps
- Requirements
- Wireframes
- Clickable prototype
- Usability validation
- Prioritized product backlog

### Phase 2: Technical Foundation

- Architecture
- Repository and development standards
- Database foundation
- Authentication and authorization
- Project and organization structure
- Environments and CI/CD
- Logging and audit foundations

### Phase 3: Core Records and Document Management

- Projects and packages
- Bored pile records
- W.I.R. records
- Attachments
- Document metadata
- Version control
- Search and filtering

### Phase 4: Digital Field and Test Workflows

- Digital field data sheets
- PIT, PDA, and CSL records
- Mobile and tablet usability
- Validation and draft handling
- Raw report upload

### Phase 5: Evaluation and GCR Review Workflow

- Evaluation reports
- Submission
- Comments
- Revisions
- NONO, NONOC C, NONOC B, and NOR statuses
- Resubmission and history

### Phase 6: Tracking, Notifications, and Dashboards

- SLA timers
- Reminders and escalations
- Dashboards
- Metrics
- Exports and reporting

### Phase 7: Hardening and User Acceptance

- Security review
- Performance testing
- Permission testing
- Data migration rehearsal
- Backup and restoration validation
- User Acceptance Testing
- User documentation and training

### Phase 8: Pilot Deployment

- Controlled launch to one project, package, team, or workflow
- Production monitoring
- User support
- Feedback collection
- Defect correction
- Success-metric review

### Phase 9: Production Rollout and Continuous Improvement

- Wider rollout
- Operations handover
- Support process
- Post-launch review
- Prioritization of Version 1 and future features

For every recommended phase, provide:

- Purpose
- Scope
- Key activities
- Deliverables
- Dependencies
- Responsible team roles
- Suggested duration or effort range
- Entry criteria
- Exit criteria
- Stakeholder validation required
- Risks
- What should explicitly not be built during that phase

Also provide:

- A roadmap table
- A dependency map
- The critical path
- Recommended milestones
- Recommended decision gates
- Features that can be developed in parallel
- Features that must be developed sequentially
- The earliest point at which a real pilot can begin
- A recommended release strategy
- A backlog for post-MVP improvements

## 18. Estimation and Resource Planning

- Recommend the roles needed for a small MVP team.
- Recommend an expanded team for faster or enterprise-scale delivery.
- Explain each role's responsibilities.
- Estimate effort or duration using ranges rather than false precision.
- State all assumptions behind estimates.
- Identify likely bottlenecks.
- Recommend how Geotechnical Engineers, Pile Test Engineers, GCR reviewers, document controllers, and other domain experts should participate.
- Recommend a realistic meeting and decision cadence.

## 19. Risk, Dependency, and Assumption Register

Create a prioritized register covering:

- Technical risks
- Security risks
- Data-quality risks
- File and document risks
- Workflow ambiguity
- Stakeholder availability
- Approval delays
- User adoption and training
- Construction-site connectivity
- Schedule and resource risks
- Infrastructure and vendor dependencies
- Migration risks
- Operational support risks

For each item, provide:

- Description
- Category
- Probability
- Impact
- Priority
- Mitigation
- Contingency
- Owner
- Phase in which it should be addressed

## 20. Success Metrics and MVP Acceptance

Recommend measurable success indicators, including:

- Reduction in manual encoding
- Reduction in missing W.I.R. attachments
- Reduction in lost or duplicated documents
- Time from testing to evaluation completion
- Time from evaluation submission to GCR decision
- Number of overdue reviews
- Data completeness and accuracy
- Time required to retrieve a bored pile's complete record
- User adoption
- User satisfaction
- System availability
- Error and failure rates

Define the overall acceptance criteria for MVP pilot readiness and full production rollout.

## 21. Open Questions and Stakeholder Decisions

Provide a prioritized list of questions that must be confirmed before or during development.

Organize the questions by:

- Business process
- Terminology
- User roles and approval authority
- Required documents
- Forms and report formats
- Status definitions
- SLA rules
- Data ownership
- Security and confidentiality
- Infrastructure
- Connectivity
- Integrations
- Migration
- Training and support
- Future expansion

For each question, identify:

- Why it matters
- Who should answer it
- The latest phase in which it must be resolved
- What provisional assumption may be used until it is answered

## 22. Additional Expert Recommendations

After completing all requested sections, independently assess the plan and provide additional recommendations.

Specifically:

- Identify important topics, features, constraints, risks, roles, workflows, or phases that were missing from the original request.
- Recommend anything that should be added, removed, delayed, simplified, or validated earlier.
- Identify over-engineering risks.
- Identify areas where the project may be under-planned.
- Recommend the smallest useful pilot.
- Recommend which uncertain or high-risk assumptions should be tested first.
- Suggest any prototype, proof of concept, technical spike, or stakeholder workshop that should occur before full development.
- Identify decisions that should remain reversible during the MVP.
- Identify decisions that would be expensive to reverse and therefore require early validation.
- Recommend whether the product should be a web application, Progressive Web App, native mobile application, or combination, based on actual field conditions.
- Recommend whether offline support is justified for the MVP.
- Recommend any appropriate future capabilities, but do not allow future ideas to inflate the MVP unnecessarily.

Do not limit the recommendations to the headings in this prompt. Add any other software-planning subject that a responsible senior development team should address.

---

# Required Final Deliverables

End the response with all of the following:

1. **Recommended MVP feature checklist**
2. **MVP versus later-phase comparison table**
3. **Recommended technology-stack summary table**
4. **High-level Mermaid architecture diagram**
5. **Initial Mermaid Entity-Relationship Diagram**
6. **Core workflow or state diagram**
7. **Recommended development-phasing table**
8. **Critical-path summary**
9. **Team and effort summary**
10. **Top ten risks**
11. **Top ten stakeholder questions**
12. **Additional expert recommendations**
13. **Recommended immediate next five actions**

The final response must be specific to the supplied Bored Pile Testing Management Tool context, actionable for a development team, and clear enough to become the starting point for requirements workshops and technical design.
