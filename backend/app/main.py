"""
FastAPI entry point for the Knowra Onboarding Agent
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Knowra Onboarding Agent API",
    description="AI-powered chatbot for employee onboarding",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Knowra Onboarding Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
