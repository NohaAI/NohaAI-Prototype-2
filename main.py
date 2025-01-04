
"""Main module for initializing the FastAPI application."""

import uvicorn
from fastapi import FastAPI
import src.api.endpoints as endpoints

# Initialize the FastAPI application
app = FastAPI()

# Include the router
app.include_router(endpoints.router)

def main():
    """Run the FastAPI application."""
    uvicorn.run(app, host="127.0.0.1", port=9090)

if __name__ == "__main__":
    main()
