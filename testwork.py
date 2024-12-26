from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from celery import Celery
from heapq import nlargest
from datetime import datetime
import os
import uuid

# FastAPI setup
app = FastAPI()

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@db:5432/transactions_db"
)
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Celery setup
celery_app = Celery("tasks", broker="redis://localhost:6379/0")

# API key for authentication
API_KEY = "secure_api_key"

def verify_api_key(api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# Models
class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "public"}  
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String)
    timestamp = Column(DateTime)

Base.metadata.create_all(bind=engine)

class TransactionInput(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    timestamp: datetime

class StatisticsResponse(BaseModel):
    total_transactions: int
    average_transaction_amount: float
    top_transactions: List[dict]

# Helper functions
def calculate_statistics():
    session = SessionLocal()
    try:
        transactions = session.query(Transaction).all()
        if not transactions:
            return {
                "total_transactions": 0,
                "average_transaction_amount": 0.0,
                "top_transactions": []
            }
        
        total_transactions = len(transactions)
        total_amount = sum(tx.amount for tx in transactions)
        average_amount = total_amount / total_transactions
        
        # Custom heap implementation to find top 3 transactions
        def heapify(arr, n, i):
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2

            if left < n and arr[left].amount > arr[largest].amount:
                largest = left

            if right < n and arr[right].amount > arr[largest].amount:
                largest = right

            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]
                heapify(arr, n, largest)

        def heap_sort(arr):
            n = len(arr)
            for i in range(n // 2 - 1, -1, -1):
                heapify(arr, n, i)

            for i in range(n - 1, n - 4, -1):
                if i <= 0:
                    break
                arr[0], arr[i] = arr[i], arr[0]
                heapify(arr, i, 0)

            return arr[-3:][::-1]

        top_transactions = heap_sort(transactions)
        top_transactions_formatted = [
            {"transaction_id": tx.id, "amount": tx.amount} for tx in top_transactions
        ]

        return {
            "total_transactions": total_transactions,
            "average_transaction_amount": round(average_amount, 2),
            "top_transactions": top_transactions_formatted
        }
    finally:
        session.close()

@celery_app.task
def update_statistics_task():
    return calculate_statistics()

# Routes
@app.post("/transactions", dependencies=[Depends(verify_api_key)])
def create_transaction(transaction: TransactionInput):
    session = SessionLocal()
    try:
        # Ensure uniqueness of transaction_id
        if session.query(Transaction).filter(Transaction.id == transaction.transaction_id).first():
            raise HTTPException(status_code=400, detail="Transaction ID already exists")

        new_transaction = Transaction(
            id=transaction.transaction_id,
            user_id=transaction.user_id,
            amount=transaction.amount,
            currency=transaction.currency,
            timestamp=transaction.timestamp
        )
        session.add(new_transaction)
        session.commit()

        task_id = str(uuid.uuid4())
        update_statistics_task.delay()

        return {"message": "Transaction received", "task_id": task_id}
    finally:
        session.close()

@app.delete("/transactions", dependencies=[Depends(verify_api_key)])
def delete_transactions():
    session = SessionLocal()
    try:
        session.query(Transaction).delete()
        session.commit()
        return {"message": "All transactions deleted"}
    finally:
        session.close()

@app.get("/statistics", response_model=StatisticsResponse, dependencies=[Depends(verify_api_key)])
def get_statistics():
    stats = calculate_statistics()
    return stats

# Automatic Swagger Documentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Financial Transaction Analysis API",
        version="1.0.0",
        description="API for managing and analyzing financial transactions",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

