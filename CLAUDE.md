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

### Hierarchical Notes Support

As of the latest version, MCP Notes supports hierarchical organization of notes:

#### Core Operations

- `add_note(title, content, tags=None, parent=None)` - Create notes with optional parent for hierarchy
- `get_note(filename)` - Retrieve notes by filename, including nested paths like "parent/child.md"
- `update_note(filename, content, tags=None)` - Update notes by filename, supports nested paths
- `delete_note(filename)` - Delete notes by filename, supports nested paths with automatic cleanup
- `list_notes(parent=None)` - List notes at specific hierarchy level

#### Hierarchical Structure

- Child notes are stored in subdirectories: `parent_name/child_name.md`
- Each directory has its own `notes_index.json` for that level only
- Support for unlimited nesting levels (parent/child/grandchild/...)
- Parent parameter accepts filenames with or without `.md` extension
- Empty directories are automatically cleaned up when last child note is deleted

#### Usage Examples

```python
# Create top-level note
add_note("Project Alpha", "Main project", ["project"])

# Create child note
add_note("Meeting Notes", "Weekly meetings", ["meetings"], parent="project_alpha")

# Access nested note
get_note("project_alpha/meeting_notes.md")

# List child notes only
list_notes(parent="project_alpha")

# Deep nesting
add_note("Action Items", "Tasks from meeting", ["tasks"], parent="project_alpha/meeting_notes")
```