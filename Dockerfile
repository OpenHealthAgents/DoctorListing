# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
# ENV OPENAI_API_KEY=... (Set this in your deployment platform)

# Run mcp_server.py using fastmcp
# Note: fastmcp run defaults to SSE. For HTTP, we might need specific flags if the platform requires it.
# However, the standard fastmcp run command is often sufficient for many MCP clients.
# If you need to expose an HTTP server (SSE), use:
#CMD ["fastmcp", "run", "mcp_server.py", "--transport", "sse", "--port", "8000", "--host", "0.0.0.0"]
CMD ["fastmcp", "run", "mcp_server.py", "--transport", "sse", "--port", "8000", "--host", "0.0.0.0"]
