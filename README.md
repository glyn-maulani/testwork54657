# Financial Transaction Analysis API

A microservice built with **FastAPI**, **PostgreSQL**, and **Redis** for managing and analyzing financial transactions.

---

## **Features**
- Add, delete, and retrieve transactions via a REST API.
- Perform transaction analysis, including:
  - Total transactions.
  - Average transaction amount.
  - Top 3 largest transactions.
- Secure endpoints with API key authentication.
- Automatically generated Swagger documentation.

---

## **Technologies Used**
- **FastAPI**: Backend framework for the REST API.
- **PostgreSQL**: Database for storing transaction data.
- **Redis**: In-memory data store for caching and task queuing.
- **Docker Compose**: Orchestrates the application and services.

---

## **Prerequisites**
Before running the application, ensure you have:
- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)

---

## **Installation and Setup**

### **1. Clone the Repository**
```bash
git clone https://github.com/glyn-maulani/testwork54657.git
cd testwork54657
```
### **2. Build and Start the Containers**
docker-compose up --build

### **3. Access the Application**
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc



