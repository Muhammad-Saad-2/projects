Technical Implementation Plan: Smart Farming Management System

    1. Android-Only Architecture

        Target Platform: Android (No iOS/Web support required).

        State Management: Provider for clean, simple dependency injection and state handling.

        Service Layer: Dedicated WeatherService, AuthService, and AppSecurityService.

    2. Authentication Design

        Providers: Firebase Email/Password and Google Sign-In.

        User Sync: Post-auth, ensure a record exists in the users Firestore collection for profile data.

    3. Data Persistence (Firestore Schema)

        app_config/status: The "Kill Switch" document. Fields: is_active (bool), message (string).

        crops: Linked to userId. Fields: name, sowingDate, expectedHarvestDate, stage, status.

        schedules: Sub-collection or linked by cropId. Fields: type (watering/treatment), frequency, nextDue.

    4. External Integrations

        Weather: Direct REST calls to Open-Meteo (lat/long based). Use a standard http client.

    5. Security Gate (The Kill Switch)

        The app must initialize the FirebaseCore and immediately execute AppSecurityService.verifyAccess().

        Navigation to the Login/Dashboard is strictly blocked if is_active is false