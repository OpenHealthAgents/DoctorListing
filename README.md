# Doctor Listing Agent

This is a ChatGPT Native App (Agent) that uses the OpenAI Agents SDK to search for doctors using the NPPES NPI Registry API.

## Prerequisites

- Python 3.9+
- OpenAI API Key

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set OpenAI API Key:**
    ```bash
    export OPENAI_API_KEY='your-api-key-here'
    ```

## Usage

### Run as a Standalone Agent

```bash
python main.py
```

### Run as an MCP Server

The project also includes an MCP server that can be used with compatible clients (like Claude Desktop or other MCP-enabled tools).

```bash
python mcp_server.py
```

Or using the FastMCP CLI:

```bash
fastmcp run mcp_server.py
```

## UI Customization

This app uses a custom UI for displaying doctor search results within ChatGPT (Inline Card).

-   **Template**: `ui/doctor_card.html`
-   **Resource**: `ui://doctor_card`

The UI is built with HTML/JS and Tailwind CSS (via CDN) and renders the structured data returned by the `search_doctors` tool.

## Deployment

### Docker

This application includes a `Dockerfile` for easy deployment to platforms like Render, Fly.io, or Google Cloud Run.

1.  **Build the image:**
    ```bash
    docker build -t doctor-listing-mcp .
    ```

2.  **Run the container:**
    ```bash
    docker run -p 8000:8000 -e OPENAI_API_KEY='your-key' doctor-listing-mcp
    ```

The MCP server will be available at `http://localhost:8000/sse` (Server-Sent Events transport).

### Platform Specifics

-   **Render/Fly.io:** Connect your repository and deploy using the Dockerfile. Ensure you set the `OPENAI_API_KEY` environment variable in the platform's dashboard.
-   **Port:** The Dockerfile is configured to expose port `8000`. Make sure your hosting platform routes traffic to this port.

## Example Queries

- "Find a cardiologist in San Francisco, CA"
- "Search for doctors named John Smith in New York"
- "Find a dentist in 90210"

## Files

- `main.py`: The entry point for the CLI agent.
- `tools.py`: Contains the `search_doctors` tool integrating with the NPPES API.
- `requirements.txt`: Python dependencies.
