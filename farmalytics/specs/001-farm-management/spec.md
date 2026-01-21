# Feature Specification: Smart Farming Management System

## Clarifications

### Session 2026-01-20
- Q: What is the exact structure of the 'Remote Kill Switch' using Firestore? → A: A dedicated Firestore document (`/app_config/status`) with a boolean field (`is_active`).
- Q: What is the strategy for the Open-Meteo API integration (no-key REST calls)? → A: Direct REST calls to Open-Meteo API endpoints (no API key required for public endpoints).
- Q: How will the 'Watering Schedule' and 'Fertilizer Tracking' be linked to specific crop documents in Firestore? → A: As sub-collections (e.g., `/crops/{cropId}/wateringSchedules`, `/crops/{cropId}/fertilizerTracking`) directly within each crop document.
- Q: What is the UI theme (Green/Nature-inspired) using Material 3? → A: Using Material 3's theming capabilities, defining a custom color scheme with green/earth tones and corresponding typography.

## User Story 1: Secure Android Application Access (P1)
As an Android user, I want to be able to securely log in with my email/password or Google account, so that I can access the farming management features.

## User Story 2: View Crop Information (P1)
As an authenticated user, I want to view a list of my crops with their details (name, sowing date, expected harvest, stage, status), so I can monitor their progress.

## User Story 3: Manage Crop Schedules (P2)
As an authenticated user, I want to manage watering and treatment schedules for my crops, so that I can ensure their healthy growth.