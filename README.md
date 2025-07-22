# Ticket Management API

This is a FastAPI application for managing tickets, users, and authentication. It includes endpoints for user registration, login, and profile management, as well as ticket creation and retrieval.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aniebietafia/ticket-management.git
    cd ticket-management
   ```
2. **Install dependencies**:
   ```bash
    pip install -r requirements.txt
   ```
3. **Set up environment variables**:
   Create a `.env` file in the root directory and add the following variables:
   ```plaintext
    JWT_SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    DATABASE_URL="postgresql+asyncpg://<username>:<password>@localhost/<database_name>"
   ```
4. **Run the application**:
   ```bash
    uvicorn main:app --reload
   ```
5. **Database Migration**:
   Ensure you have a PostgreSQL database set up and run the migrations:
   ```bash
    alembic upgrade head
   ```
6. **Access the API**:
   Open your browser and go to `http://localhost:8000/docs` to access the Swagger UI for API documentation and testing.
