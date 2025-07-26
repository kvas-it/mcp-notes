# MCP Notes

MCP Notes is an MCP (Model Context Protocol) server for managing notes. It stores tagged and interlined notes in a directory of markdown files and exposes tools to manage them. The project is written in Python using FastMCP.

## Development Setup

### Virtual Environment

The project uses a Python virtual environment located in the `venv/` directory.

To activate the virtual environment:
```bash
source venv/bin/activate
```

The project is installed in editable mode, so changes to the code are immediately available.

### Running the Server

To run the MCP Notes server:
```bash
mcp-notes --dir /path/to/notes/directory
```

### Testing

Run tests using pytest:
```bash
venv/bin/python -m pytest
```

### Linting and Formatting

Run the linter:
```bash
venv/bin/python -m ruff check
```

Format the Python code:
```bash
venv/bin/python -m ruff format
```

Note: `ruff format` only formats Python code files, not markdown or other text files.

Fix linting issues automatically:
```bash
venv/bin/python -m ruff check --fix
```

## Project Structure

- `mcp_notes/` - Main application package
- `mcp_notes/storage.py` - Storage class for managing note files
- `mcp_notes/mcp_server.py` - FastMCP server setup and tools
- `mcp_notes/__main__.py` - CLI entry point
- `tests/` - Test files for storage and MCP server functionality
- `pyproject.toml` - Project dependencies and metadata
- `ruff.toml` - Linting and formatting configuration

## API Changes

### Filename-Only Operations

As of the latest version, the following operations require only a filename parameter:

- `get_note(filename)` - Retrieve a note by filename
- `update_note(filename, content, tags=None)` - Update a note by filename
- `delete_note(filename)` - Delete a note by filename

The `add_note(title, content, tags=None)` operation still uses titles to generate filenames automatically. The `list_notes()` operation returns metadata for all notes including both filename and title.