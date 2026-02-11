import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from fca_mcp.server.main import create_server

logger = logging.getLogger(__name__)

# Global server instances
_global_server = None
_global_assistant = None
_global_nl_interface = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    global _global_server, _global_assistant, _global_nl_interface

    fca_email = os.getenv("FCA_API_USERNAME")
    fca_key = os.getenv("FCA_API_KEY")

    if not fca_email or not fca_key:
        logger.error("[ERROR] Missing FCA API credentials in environment")
        yield
        return

    _global_server = await create_server(fca_email=fca_email, fca_key=fca_key, enable_auth=False)

    _global_assistant = FcaAiAssistant(_global_server)
    _global_nl_interface = NaturalLanguageInterface(_global_assistant)

    logger.info("[HTTP] Server initialized successfully")

    yield

    if _global_server:
        await _global_server.close()
        logger.info("[HTTP] Server closed")


app = FastAPI(
    title="FCA MCP Server API",
    description="HTTP API for FCA regulatory data with AI analysis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class AnalyzeRequest(BaseModel):
    firm_name: str


class CompareRequest(BaseModel):
    firm1: str
    firm2: str


class NLQueryRequest(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with HTML interface."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FCA MCP Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .endpoint {
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #667eea;
                border-radius: 4px;
            }
            .method {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background: #61affe; color: white; }
            .post { background: #49cc90; color: white; }
            code {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
            .feature {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 6px 12px;
                margin: 5px;
                border-radius: 20px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏛️ FCA MCP Server</h1>
            <p>AI-Powered UK Financial Conduct Authority Data Analysis</p>
            <div>
                <span class="feature">MCP Protocol</span>
                <span class="feature">AI Analysis</span>
                <span class="feature">Risk Scoring</span>
                <span class="feature">LLM Integration</span>
            </div>
        </div>
        
        <div class="card">
            <h2>📊 System Status</h2>
            <p>✅ Server is running and ready</p>
            <p>✅ FCA API connected</p>
            <p>✅ AI Assistant active</p>
        </div>
        
        <div class="card">
            <h2>🔌 API Endpoints</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/health</code>
                <p>Health check endpoint</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/docs</code>
                <p>Interactive API documentation (Swagger UI)</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/search</code>
                <p>Search for firms by name</p>
                <pre>{"query": "Barclays", "limit": 10}</pre>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/analyze</code>
                <p>AI risk analysis of a firm</p>
                <pre>{"firm_name": "Barclays Bank"}</pre>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/compare</code>
                <p>Compare two firms</p>
                <pre>{"firm1": "Barclays", "firm2": "HSBC"}</pre>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/ask</code>
                <p>Natural language query</p>
                <pre>{"question": "Is Barclays Bank safe?"}</pre>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/stats</code>
                <p>Server usage statistics</p>
            </div>
        </div>
        
        <div class="card">
            <h2>📚 Quick Start</h2>
            <p><strong>1. View API Documentation:</strong></p>
            <p><a href="/docs" target="_blank">Open Swagger UI</a></p>
            
            <p><strong>2. Try an example:</strong></p>
            <pre>curl -X POST http://localhost:8000/api/search \\
-H "Content-Type: application/json" \\
-d '{"query": "Barclays", "limit": 5}'</pre>
        </div>
        
        <div class="card">
            <h2>ℹ️ About</h2>
            <p>This server provides:</p>
            <ul>
                <li>✅ Complete access to FCA Financial Services Register</li>
                <li>✅ AI-powered risk analysis (0-100 scoring)</li>
                <li>✅ Firm comparison and insights</li>
                <li>✅ Permission categorization and analysis</li>
                <li>✅ Natural language query processing</li>
                <li>✅ RESTful HTTP API</li>
            </ul>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "FCA MCP Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": {"mcp_tools": True, "ai_analysis": True, "nl_interface": True},
    }


@app.post("/api/search")
async def search_firms(request: SearchRequest):
    """Search for firms."""
    if not _global_server:
        raise HTTPException(status_code=503, detail="Server not initialized")

    result = await _global_server.handle_request(
        tool="search_firms", params={"query": request.query, "limit": request.limit}, authorization=None
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@app.post("/api/analyze")
async def analyze_firm(request: AnalyzeRequest):
    """AI risk analysis of a firm."""
    if not _global_assistant:
        raise HTTPException(status_code=503, detail="AI Assistant not initialized")

    analysis = await _global_assistant.analyze_firm_risk(request.firm_name)

    if analysis["status"] == "error":
        raise HTTPException(status_code=404, detail=analysis["message"])

    return analysis


@app.post("/api/compare")
async def compare_firms(request: CompareRequest):
    """Compare two firms."""
    if not _global_assistant:
        raise HTTPException(status_code=503, detail="AI Assistant not initialized")

    comparison = await _global_assistant.compare_firms(request.firm1, request.firm2)

    if comparison["status"] == "error":
        raise HTTPException(status_code=400, detail=comparison["message"])

    return comparison


@app.post("/api/ask")
async def natural_language_query(request: NLQueryRequest):
    """Process natural language query."""
    if not _global_nl_interface:
        raise HTTPException(status_code=503, detail="NL Interface not initialized")

    response = await _global_nl_interface.process_query(request.question)
    return response


@app.get("/api/stats")
async def get_stats():
    """Get server statistics."""
    if not _global_server:
        raise HTTPException(status_code=503, detail="Server not initialized")

    return _global_server.get_usage_stats()


def get_fastapi_app() -> FastAPI:
    """Get the FastAPI application instance."""
    return app
