# FastMCP Testing Guide

## Overview

This document summarizes key testing patterns for FastMCP applications.

**Reference:** https://gofastmcp.com/patterns/testing

## Key Testing Patterns

### In-Memory Testing (Recommended)

The most efficient method is passing the FastMCP server instance directly to a Client:

```python
@pytest.fixture
def mcp_server():
    server = FastMCP("TestServer")

    @server.tool
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    return server

async def test_tool_functionality(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("greet", {"name": "World"})
        assert result.data == "Hello, World!"
```

### Configuration for Async Tests

For async tests with pytest, configure `asyncio_mode = "auto"` in your pytest configuration.

### Mocking

FastMCP servers work seamlessly with standard Python testing tools and patterns. You can use familiar Python mocking, patching, and testing techniques.

## Best Practices

1. **Direct client-server connections** - Create direct connections for efficient testing without starting separate server processes
2. **Standard Python patterns** - Leverage existing Python testing frameworks and techniques
3. **Fixture-based setup** - Use pytest fixtures to set up test servers with appropriate state

## Implementation in This Project

See `test_mcp_server.py` for examples of these patterns applied to the MCP Notes server, including:
- Setting up temporary storage for each test
- Testing all CRUD operations through MCP tools
- Error handling and edge case testing
