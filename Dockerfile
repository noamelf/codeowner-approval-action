# Use the official Python image from the Docker library
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy the script into the Docker image
COPY check_code_owners_approval.py /usr/local/bin/check_code_owners_approval.py

# Set the entrypoint to the script
ENTRYPOINT ["uv", "run", "/usr/local/bin/check_code_owners_approval.py"]
