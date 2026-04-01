# Backend

This backend powers the ChatKit demo and is split into two running processes:

- the ChatKit HTTP server in [main.py](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/main.py), exposed on `http://127.0.0.1:8000/chatkit`
- the local MCP server in [mcp_server.py](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/mcp_server.py), exposed on `http://127.0.0.1:8001/mcp`

The chat server uses the OpenAI Agents SDK plus ChatKit. When the agent needs product data, it calls the local MCP server. Product messages are also rendered as a ChatKit widget.

## Structure

- [app/chatkit_app.py](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/app/chatkit_app.py): FastAPI app and `/chatkit` route
- [app/assistant.py](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/app/assistant.py): agent definition and the `show_store_products` tool
- [app/mcp.py](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/app/mcp.py): MCP client setup and FastAPI lifespan hooks
- [app/products.py](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/app/products.py): product loading and widget shaping
- [app/store.py](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/app/store.py): simple JSON-backed ChatKit store in `backend/chatkit_store.json`
- [app/widgets/simple_product.widget](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/app/widgets/simple_product.widget): widget template used to render products
- [mcp_server.py](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/mcp_server.py): local MCP server with the `list_products` tool

## Requirements

- Python 3.13
- `OPENAI_API_KEY` in [backend/.env](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/.env)

Example:

```env
OPENAI_API_KEY=your_api_key_here
```

## Install

Install dependencies with `uv`:

```bash
cd backend
uv sync
```

## Run Locally

Start the MCP server in one terminal:

```bash
cd backend
uv run uvicorn mcp_server:mcp.streamable_http_app --factory --host 127.0.0.1 --port 8001 --reload
```

Start the ChatKit backend in a second terminal:

```bash
cd backend
uv run python main.py
```

If you want reload mode for the ChatKit backend as well:

```bash
cd backend
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will connect to the MCP server using:

```bash
STORE_MCP_URL=http://127.0.0.1:8001/mcp
```

That is already the default, so you usually do not need to set it manually.

## Frontend

The frontend dev server lives in `../frontend` and proxies `/chatkit` to the backend on port `8000`.

From the repo root:

```bash
cd frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:5173
```

## Notes

- Chat threads and thread items are persisted to [chatkit_store.json](/Users/alexander.kornyukhin/Projects/experiments/chatkit_demo/backend/chatkit_store.json)
- Product data currently comes from the local in-file MCP tool, not a database
- If you ask the assistant to show or list products, it should call the backend tool and render the product widget
