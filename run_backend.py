"""Start the AIHawk HTTP API server."""

import uvicorn

import config


def main() -> None:
    print(f"Starting AIHawk backend at {config.BACKEND_URL}")
    print(f"API docs:     {config.BACKEND_URL}/docs")
    print(f"Health check: {config.BACKEND_URL}/health")
    print(f"Verity ready: {config.BACKEND_URL}/api/v1/verity/ready")
    uvicorn.run(
        "src.api.server:app",
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()
