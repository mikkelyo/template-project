"""FastAPI application entry point."""

from fastapi import FastAPI

import uvicorn

from template_project.di_container import InfrastructureContainer, ServicesContainer
from endpoints.health import health


# Initialize DI containers
infrastructure = InfrastructureContainer()
services = ServicesContainer(infrastructure=infrastructure)

# Create FastAPI app
app = FastAPI(title="Template Project API", version="0.1.0")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return await health()


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
