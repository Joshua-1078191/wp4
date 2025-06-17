# RAcademic App

A platform for students to share and discover study resources.

## Quick Start with Docker

The easiest way to run the application is using Docker. Make sure you have [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Start the application:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

That's it! The application should now be running with both frontend and backend services.

## Manual Setup (Alternative)

If you prefer to run the services without Docker, follow these instructions:

### Prerequisites
- [Node.js](https://nodejs.org/) (version 14 or higher)
- [Python](https://www.python.org/) (version 3.8 or higher)
- [Git](https://git-scm.com/) (for cloning the repository)

### Backend Setup
```bash
cd app/backend

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn main:app --reload
```

### Frontend Setup
```bash
# In a new terminal
cd app

# Install Node.js dependencies
npm install

# Start the frontend development server
npm start
```

## Testing the Application

1. Open http://localhost:3000 in your browser
2. You should see the login page
3. Click "Register" to create a new account
   - Use an @hr.nl email address
   - Create a password
   - Enter a display name
4. After registration, you'll be redirected to the login page
5. Log in with your credentials

## Troubleshooting

### Docker Issues
- Make sure Docker and Docker Compose are installed correctly
- Check if ports 3000 and 8000 are available
- Try rebuilding the containers: `docker-compose up --build`
- Check container logs: `docker-compose logs`

### Manual Setup Issues
- Make sure Python and pip are installed correctly
- Check if the virtual environment is activated
- Verify all requirements are installed
- Ensure ports 3000 and 8000 are not in use

## Project Structure
```
.
├── app/                # Frontend application
│   ├── public/        # Static files
│   ├── src/          # React source code
│   │   ├── pages/    # React components
│   │   └── ...
│   ├── backend/      # Python backend
│   │   ├── main.py   # FastAPI application
│   │   └── ...
│   ├── Dockerfile    # Frontend Docker configuration
│   └── package.json  # Node.js dependencies
├── docker-compose.yml # Docker services configuration
└── README.md         # This file
```

## Support

If you encounter any issues:
1. Check the troubleshooting section
2. Verify Docker is running correctly
3. Check the container logs
4. Make sure all required ports are available 