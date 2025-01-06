# E-Commerce Authentication System

This project is an authentication system for an e-commerce platform, implemented with FastAPI for the backend and Streamlit for the frontend. It uses JWT (JSON Web Tokens) for secure user authentication and OAuth2 for token management. The project integrates PostgreSQL for data storage and uses Poetry for package management.

## Key Features

- **User Registration**: Allows users to create an account by providing their email, password, and other details.
- **Login**: Authenticated users can log in with their credentials, generating access and refresh tokens.
- **Password Hashing**: User passwords are securely hashed using `bcrypt` before being stored in the database.
- **JWT Authentication**: The system uses JWT for securing API endpoints and handling authentication.
- **Session Management**: Tokens are stored in cookies, and users can log out by deleting the tokens from the browser.
- **OAuth2 Integration**: OAuth2 flow is used to manage access and refresh tokens for secure user authentication.
- **PostgreSQL Database**: User data and authentication details are stored in a PostgreSQL database.

## Backend Implementation

The backend is built using **FastAPI**, a modern web framework for building APIs. The backend includes the following:

### 1. User Registration:
- When a user registers, their password is hashed using `bcrypt` and stored securely in the PostgreSQL database.
- A new user is created in the database with details like email, password hash, and user role.

### 2. Login and Token Generation:
- Upon login, the user's credentials are verified, and if valid, JWT tokens (access and refresh) are generated.
- The **access token** is short-lived and used for authentication, while the **refresh token** is used to obtain a new access token when it expires.
- The tokens are returned to the frontend and saved in the browser cookies for session management.

### 3. Password Hashing:
- Passwords are hashed using the `bcrypt` hashing algorithm, ensuring that sensitive user data is not stored in plaintext.

### 4. OAuth2 and JWT:
- OAuth2 is implemented with **password grant flow** to handle user login and token management.
- JWT tokens are used for authenticating API requests, ensuring that only authorized users can access protected routes.
- The backend also supports **refresh tokens**, allowing users to stay logged in without having to re-enter their credentials frequently.

### 5. PostgreSQL Integration:
- PostgreSQL is used to store user information, including hashed passwords and token details. 
- The database schema is designed to handle user roles and authentication data securely.

## Frontend Implementation

The frontend is built using **Streamlit**, a simple and fast framework for creating interactive web applications. The frontend handles user login, registration, and session management as follows:

### 1. User Login:
- The user provides their email and password, which are sent to the backend to generate JWT tokens.
- If the credentials are valid, the tokens are saved in the browser cookies for session management.

### 2. User Registration:
- Users can sign up by providing their email, full name, and password.
- The registration form sends the details to the backend, which creates a new user record in the PostgreSQL database.

### 3. Session Management:
- The frontend uses cookies to store JWT tokens (`auth_token` and `refresh_token`) securely.
- The session is considered authenticated when the `auth_token` is present in the cookies, and the user's information is fetched from the backend.
- Users can log out by deleting the tokens from the cookies, which is handled by the logout function.

### 4. Logout:
- The logout function deletes the JWT tokens from the cookies and clears the session state.
- The user is redirected to the login page after logging out.

## Database Integration (PostgreSQL)

The system uses **PostgreSQL** to store user information securely. The database stores the following:

- **User Table**: Contains user details such as email, password hash, and role.
- **Password Hashing**: User passwords are hashed using the `bcrypt` algorithm before storing them in the database.

## Security Features

- **JWT Authentication**: Secure token-based authentication using JSON Web Tokens (JWT). The tokens are stored in cookies and used for accessing protected API routes.
- **Password Hashing**: User passwords are hashed with `bcrypt` before storing them in the database, ensuring security.
- **Session Management**: Tokens are stored securely in cookies with expiration times to manage user sessions.
- **OAuth2 Integration**: OAuth2 is used for managing authentication flows, allowing for secure access token generation and refreshing.

## Technologies Used

- **Backend**: FastAPI, OAuth2, JWT, PostgreSQL
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **Password Hashing**: bcrypt
- **Package Management**: Poetry
- **Environment Variables**: dotenv

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/https://github.com/Muhammad-Saad-2/projects.git
