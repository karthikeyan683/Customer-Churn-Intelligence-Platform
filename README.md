Customer Churn Intelligence & Prediction Platform

An end-to-end customer analytics platform designed to identify customers at risk of leaving, generate churn predictions, and support data-driven retention decisions.

Overview

The Customer Churn Intelligence & Prediction Platform combines customer data management, machine learning, analytics, and secure API access in one application.

The project demonstrates how machine learning can help businesses understand customer churn risk and make informed customer-retention decisions.

 Key Features

- **Customer Management** — Create, view, search, and update customer records.
- **Churn Prediction** — Generate customer-level churn probabilities and risk classifications.
- **Prediction History** — Store and retrieve previous predictions for individual customers.
- **Prediction Explanations** — Provide explanations for churn predictions through the prediction API.
- **Analytics Dashboard** — Present customer and churn-related information through a React interface.
- **Authentication & Authorization** — JWT-based authentication and role-based access for analysts and administrators.
- **Audit Logging** — Record relevant application activities with restricted access to audit logs.
- **REST API** — FastAPI endpoints with interactive API documentation.
- **Responsive Frontend** — A React-based interface designed for desktop and mobile screens.

 Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, Axios |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Machine Learning | Python-based churn prediction |
| Authentication | JWT |
| API Documentation | Swagger UI, OpenAPI |
| Version Control | Git, GitHub |

Project Structure

text
ChurnIntelligence/
├── backend/       # FastAPI application and backend services
├── database/      # Database-related resources
├── docs/          # Project documentation
├── frontend/      # React and Vite application
├── ml/            # Machine learning resources
├── tests/         # Automated tests
├── .gitignore
└── README.md


 Application Architecture

text
User
 |
 v
React Frontend
 |
 | HTTP requests with Axios
 | JWT authentication
 v
FastAPI Backend
 |
 +---- Authentication & Authorization
 |
 +---- Customer Management
 |
 +---- Churn Prediction Services
 |
 +---- Prediction History & Audit Logs
 |
 v
PostgreSQL Database


The frontend communicates with the backend through REST APIs. The backend handles authentication, business logic, database operations, and churn prediction requests.

Getting Started

 Prerequisites

Install the following tools:

- Python
- Node.js and npm
- PostgreSQL
- Git

 1. Clone the Repository

bash
git clone https://github.com/karthikeyan683/Customer-Churn-Intelligence-Platform.git
cd Customer-Churn-Intelligence-Platform


 2. Configure the Backend

Open a terminal in the project directory:
powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt


Configure the backend environment variables using the project's existing settings and a local PostgreSQL database. Do not commit passwords, secret keys, access tokens, or database credentials.

If the project uses Alembic migrations, apply the available migrations according to the backend configuration.

Start the API:

powershell
uvicorn app.main:app --reload


The API should be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

 3. Configure the Frontend

Open a second terminal:

powershell
cd frontend
npm install


Create or update `frontend/.env` with the URL of your local backend:

dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000


Start the frontend:
powershell
npm run dev


Open the local URL printed by Vite in your browser.

**Note:** The backend and database must be configured before the frontend can retrieve real application data. Use the authentication flow supported by the backend to register or sign in.

Security Considerations

- Keep credentials and secret keys out of source control.
- Use environment variables for environment-specific configuration.
- Protect API endpoints with appropriate authentication and authorization.
- Restrict administrator-only operations to authorized roles.
- Avoid exposing sensitive customer information in logs or API responses.

Project Goals

- Apply machine learning to a practical business problem.
- Build a full-stack application using React and FastAPI.
- Integrate a relational database with backend services.
- Implement authentication and role-based authorization.
- Present customer insights through a responsive user interface.
- Demonstrate software engineering, API development, and machine-learning integration.


