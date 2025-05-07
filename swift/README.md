# Twitter Clone - Microservices Architecture

A Twitter-like application built with FastAPI, React, and a microservices architecture.

## Features

- User authentication and authorization
- Real-time post updates using WebSocket
- Like and comment functionality
- Follow/unfollow system
- Real-time notifications
- Modern and responsive UI

## Architecture

The application is built using a microservices architecture with the following services:

1. **Auth Service** (Port 8001)
   - Handles user authentication and registration
   - JWT token generation and validation

2. **Posts Service** (Port 8002)
   - Manages posts, likes, and comments
   - Real-time updates using WebSocket

3. **Notifications Service** (Port 8003)
   - Handles user notifications
   - Real-time notification delivery

4. **Users Service** (Port 8004)
   - Manages user profiles and relationships
   - Follow/unfollow functionality

5. **API Gateway** (Port 8000)
   - Routes requests to appropriate services
   - Handles CORS and request forwarding

## Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB
- PostgreSQL
- Redis (optional, for caching)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd twitter-clone
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the database URLs and other configuration

## Running the Application

1. Start all backend services:
   ```bash
   ./run_services.sh
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

3. Access the application at `http://localhost:3000`

## API Documentation

Once the services are running, you can access the API documentation at:
- Auth Service: `http://localhost:8001/docs`
- Posts Service: `http://localhost:8002/docs`
- Notifications Service: `http://localhost:8003/docs`
- Users Service: `http://localhost:8004/docs`
- API Gateway: `http://localhost:8000/docs`

## Development

- Backend services are written in Python using FastAPI
- Frontend is built with React and TailwindCSS
- Real-time features use WebSocket
- Database: MongoDB for posts and notifications, PostgreSQL for users and relationships

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
