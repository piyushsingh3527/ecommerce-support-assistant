# AI-Powered E-Commerce Catalog, Order and Customer Support Assistant

A FastAPI-based e-commerce backend with product and order management, customer support tickets, authentication, role-based access control, and an AI-powered knowledge-base chatbot using RAG (Retrieval-Augmented Generation).

## Features

* User registration and login
* JWT-based authentication
* Role-based access control
  * Admin
  * Support Staff
  * Customer
* Category CRUD
* Product CRUD
* Product price and stock management
* JSONB product specifications
* Customer profile management
* Order and order-item management
* Server-side order total calculation
* Stock validation before order creation
* Controlled order status transitions
* Customer support tickets
* Approved document upload
* PDF, DOCX, TXT and Markdown document processing
* Text chunking
* Sentence-transformer embeddings
* PostgreSQL with pgvector for vector search
* RAG-based customer support chatbot
* Source references in chatbot answers
* Protection of other customers' order information
* No-answer behavior when information is not available
* WebSocket browser chat
* Swagger/OpenAPI documentation
* Automated tests with pytest
* Alembic database migrations

## Technology Stack

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* pgvector
* Alembic
* JWT
* Argon2 password hashing
* Sentence Transformers
* Groq API
* PyMuPDF
* python-docx
* pytest
* WebSockets

## Project Structure

```text
ecommerce-support-assistant/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── llm/
│   ├── schemas/
│   ├── services/
│   ├── static/
│   ├── websocket/
│   └── main.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── data/
│   ├── knowledge_base/
│   ├── storage/
│   └── vector_index/
│
├── docker/
│   └── init.sql
│── docs/
├── scripts/
├── tests/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── README.md
```

## Requirements

Install:

* Python 3.13+
* PostgreSQL 18+
* Git
* Docker Desktop

Groq API key needed.

## Setup

Clone the repository.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the requirements:

```powershell
pip install -r requirements.txt
```

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Copy `.env.example` to `.env` and update the required values.

Never commit `.env` or any secret/API key to GitHub.

## Database Setup

Create the PostgreSQL database:

```sql
CREATE DATABASE ecommerce_support;
```

Run the database migrations:

```powershell
alembic upgrade head
```

Check the current migration:

```powershell
alembic current
```

## Create Admin User

Run:

```powershell
python -m scripts.create_admin
```

## Run Application

### Run locally

Start the FastAPI application:

```powershell
uvicorn app.main:app --reload
```

The application will run at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Docker Setup

Docker Compose can be used to run the FastAPI application and PostgreSQL database together.

Build and start the containers:

```powershell
docker compose up --build
```

The FastAPI application will be available at:

```text
http://127.0.0.1:8080
```

Swagger documentation:

```text
http://127.0.0.1:8080/docs
```

The Docker PostgreSQL database is exposed on port `5433`.

Docker Compose automatically runs the Alembic migrations before starting the FastAPI application.

To create the admin user inside the Docker container:

```powershell
docker compose exec app python -m scripts.create_admin
```

To stop the containers:

```powershell
docker compose down
```

## API Endpoints

### Health

```text
GET /health
GET /me
```

### Authentication

```text
POST /auth/register
POST /auth/login
```

### Categories

```text
GET /categories/
POST /categories/
GET /categories/{category_id}
PUT /categories/{category_id}
DELETE /categories/{category_id}
```

### Products

```text
GET /products/
POST /products/
GET /products/{product_id}
PUT /products/{product_id}
DELETE /products/{product_id}
```

### Customers

```text
GET /customers/
POST /customers/
PUT /customers/
DELETE /customers/
```

### Orders

```text
GET /orders/
POST /orders/
GET /orders/{order_id}
DELETE /orders/{order_id}
PUT /orders/{order_id}/status
```

### Support Tickets

```text
GET /tickets/
POST /tickets/
GET /tickets/{ticket_id}
PUT /tickets/{ticket_id}
DELETE /tickets/{ticket_id}
PATCH /tickets/{ticket_id}/status
```

### Knowledge Documents

```text
POST /documents/upload
GET /documents/
DELETE /documents/{document_id}
POST /documents/{document_id}/reindex
```

### Chat

```text
POST /chat/
```

WebSocket:

```text
/ws/chat
```

Browser chat:

When running locally:

```text
http://127.0.0.1:8000/static/chat.html
```

When running with Docker:
```text
http://127.0.0.1:8080/static/chat.html
```
## RAG Workflow

The chatbot follows this general workflow:

```text
User Question
      ↓
Query Embedding
      ↓
PostgreSQL + pgvector
      ↓
Relevant Document Chunks
      ↓
Context
      ↓
LLM
      ↓
Answer + Source Reference
```

The chatbot should not invent:

* Product price
* Product stock
* Delivery date
* Return eligibility
* Warranty terms

If the required information is not available in the knowledge base, the chatbot returns a clear no-answer response.

## Order Data Protection

Order information is retrieved from the database using permission checks instead of being invented by the LLM.

Customers can access their own orders.

Support staff can access permitted orders.

Administrators can access permitted order information.

The chatbot must not expose another customer's order information.

## Testing

Run the tests locally:

```powershell
pytest -q
```

Run the tests inside Docker:

```powershell
docker compose exec app pytest -q
```

Current Docker test result:

```text
15 passed
```
The project test suite covers areas including:

Authentication
Role-based access
Categories
Products
Customers
Orders
Stock validation
Order status transitions
Support tickets
Chat behavior
Order data protection

The current Docker test suite passes all implemented tests.

## Database Migrations

Create a new migration:

```powershell
alembic revision --autogenerate -m "description"
```

Apply migrations:

```powershell
alembic upgrade head
```

Check migration history:

```powershell
alembic history
```

Check the current migration:

```powershell
alembic current
```

## Security

* Keep `.env` out of GitHub.
* Never commit passwords or API keys.
* JWT is used for authentication.
* Passwords are stored using Argon2 hashing.
* Role-based access control is used for protected operations.
* Order ownership and permissions are checked before returning order information.

## Scope

This is an educational project.

The project uses sample product data and support documents.

Checkout is mocked and does not use a real payment gateway.

The project does not connect to a live commercial e-commerce database.

## Future Improvements

* Shopping cart
* Coupon system
* Product comparison
* Low-stock dashboard
* Chat history
* Document management dashboard
* CI/CD with GitHub Actions
* More extensive API/integration tests

👨‍💻 Author

Piyush Singha

College Project — BCA(H)
Python, FastAPI and AI Engineering

📜 License

This project is developed for educational and academic purposes.