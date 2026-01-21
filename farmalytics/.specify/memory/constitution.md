<!-- Sync Impact Report -->
<!--
Version change: 0.0.0 → 1.0.0
Modified principles: None (initial creation/major update)
Added sections: Security & Control, Tech Stack, Cost Efficiency, Architecture, Simplicity, Handover-Ready
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending
- .specify/templates/spec-template.md: ⚠ pending
- .specify/templates/tasks-template.md: ⚠ pending
- .specify/templates/commands/*.md: ⚠ pending
Follow-up TODOs: None
-->
# Farmalytics App Constitution

## Core Principles

### I. Security & Control (Remote Kill Switch)
The app MUST implement a "Remote Kill Switch." On every app launch, it must check a Firestore document `app_config/status`. If `is_active` is `false`, the app must show a non-dismissible "Demo Expired" screen.
Rationale: Ensures the ability to remotely disable the application, crucial for managing demo access and security.

### II. Tech Stack
The application MUST use Flutter for the Frontend and Firebase (Auth/Firestore) for the Backend.
Rationale: Standardizes development on proven technologies for efficient development and consistent maintainability.

### III. Cost Efficiency
The application MUST use only free-tier Firebase features and Open-Meteo for weather data (no paid API keys).
Rationale: Ensures the project remains cost-effective and avoids unexpected expenses, aligning with academic project constraints.

### IV. Architecture
The application MUST use a feature-first folder structure (e.g., `lib/features/crop`, `lib/features/weather`, etc.).
Rationale: Promotes modularity, improves code organization, and simplifies feature development and maintenance.

### V. Simplicity
This is for an FYP presentation. Prioritize a clean, functional UI over complex animations.
Rationale: Focuses development efforts on core functionality and usability, ensuring a clear demonstration for the final year project.

### VI. Handover-Ready
Code MUST be commented such that ownership can be transferred to the client by simply changing the Firebase project ID/Owner.
Rationale: Facilitates easy project handover and future maintenance by providing clear documentation and minimal setup changes.

## Governance
This Constitution supersedes all other project practices. Amendments require documentation, approval, and a migration plan.

All pull requests and code reviews MUST verify compliance with these principles. Complexity must be justified.

**Version**: 1.0.0 | **Ratified**: 2026-01-17 | **Last Amended**: 2026-01-17
