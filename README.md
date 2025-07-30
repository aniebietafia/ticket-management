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
4. **Activate Virtual Environment**:
   ```bash
      source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
5. **Run the application**:
   ```bash
    uvicorn main:app --reload
   ```
6. **Database Migration**:
   Ensure you have a PostgreSQL database set up and run the migrations:

   ```bash
   # Initialize Alembic
   alembic init alembic

   # Update alembic.ini with your database URL
   # In alembic.ini, set the sqlalchemy.url to your DATABASE_URL
   sqlalchemy.url = postgresql+asyncpg://<username>:<password>@localhost/<database_name>

   # Update the env.py file in the alembic directory to include your models
   from app.models import Base  # Adjust the import based on your project structure
   target_metadata = Base.metadata

   # Generate migration files
   alembic revision --autogenerate -m "Initial migration"

   # Apply migrations
    alembic upgrade head
   ```

7. **Install pytest**:
   If you haven't already, install `pytest` for running tests.

   ```bash
   pip install pytest
   ```

8. **Run Tests**:
   Ensure you have `pytest` installed and run the tests to verify everything is working correctly.

   ```bash
   pytest
   ```

9. **Access the API**:
   Open your browser and go to `http://localhost:8000/docs` to access the Swagger UI for API documentation and testing.
