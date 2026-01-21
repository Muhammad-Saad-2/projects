# Tasks: Smart Farming Management System

## Phase 1: Foundation & Security
- [ ] **T001: Project Scaffolding**
  - Initialize Flutter project (Android only).
  - Add dependencies: `firebase_core`, `cloud_firestore`, `firebase_auth`, `google_sign_in`, `provider`.
  - Place `google-services.json` in `android/app/`.

- [ ] **T002: Remote Kill Switch (CRITICAL)**
  - Create `AppSecurityService` to fetch `app_config/status` from Firestore.
  - Implement a `LockScreen` that displays the message from Firestore if `is_active` is false.
  - Acceptance Criteria: App must show LockScreen before Login if disabled in Console.

## Phase 2: Authentication
- [ ] **T003: Email/Password Auth**
  - Build Login and Signup UI.
  - Implement Firebase Auth logic for email/password.

- [ ] **T004: Google Sign-In**
  - Implement Google Sign-In button and logic.
  - Acceptance Criteria: User profile doc is created in `users/` collection on first login.

## Phase 3: Core Features
- [ ] **T005: Weather Integration**
  - Create `WeatherService` using Open-Meteo REST API.
  - Build Dashboard widget showing Temp, Humidity, and Wind.

- [ ] **T006: Crop Management (CRUD)**
  - Build 'Add Crop' form and 'Active Crops' list.
  - Implement growth stage updates and 'Harvest' status toggle.

## Phase 4: Scheduling & Final APK
- [ ] **T007: Watering & Treatment Logs**
  - Implement history logs for fertilizers/pesticides.
  - Add basic "due today" alerts on the dashboard.

- [ ] **T008: Release Preparation**
  - Run `./gradlew signingReport` to verify SHA-1 for Google Sign-In.
  - Build release APK: `flutter build apk --release`.