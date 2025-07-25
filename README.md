# MCP Notes

MCP Notes is an MCP (Model Context Protocol) server for managing notes. It stores tagged notes in a directory of markdown files and exposes tools to manage them through the Model Context Protocol.

## Features

- **Add Notes**: Create new notes with titles, content, and tags
- **Retrieve Notes**: Get notes by title or filename
- **List Notes**: View all notes with their metadata
- **Delete Notes**: Remove notes by title or filename
- **Tag Support**: Organize notes with customizable tags
- **File-based Storage**: Notes are stored as markdown files in a specified directory
- **JSON Index**: Fast lookups using a JSON index file

## Installation

Install the package using pip:

```bash
pip install .
```

For development, install with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

### Running the Server

Start the MCP Notes server by specifying a directory to store notes:

```bash
mcp-notes --dir /path/to/notes/directory
```

The server will create the directory if it doesn't exist and start listening for MCP connections.

### Available Tools

The server exposes the following MCP tools:

#### `add_note`
Add a new note with title, content, and optional tags.

**Parameters:**
- `title` (str): The note title
- `content` (str): The note content
- `tags` (List[str], optional): List of tags for the note

**Example:**
```python
add_note(
    title="Meeting Notes",
    content="Discussed project timeline and deliverables",
    tags=["work", "meetings"]
)
```

#### `get_note`
Retrieve a note by title or filename.

**Parameters:**
- `title` (str, optional): The note title
- `filename` (str, optional): The note filename

Note: Either `title` or `filename` must be provided.

#### `list_notes`
List all notes with their metadata.

**Returns:** List of note information including filename, title, and tags.

#### `delete_note`
Delete a note by title or filename.

**Parameters:**
- `title` (str, optional): The note title
- `filename` (str, optional): The note filename

Note: Either `title` or `filename` must be provided.

## File Structure

Notes are stored as markdown files with the following format:

```markdown
# Note Title
Tags: tag1, tag2, tag3

Note content goes here...
```

The server maintains a `notes_index.json` file in the notes directory for fast lookups.

## Development

### Setup

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

Run the test suite using pytest:

```bash
python -m pytest
```

### Code Quality

Format code using ruff:

```bash
python -m ruff format
```

Run linting:

```bash
python -m ruff check
```

Auto-fix linting issues:

```bash
python -m ruff check --fix
```

### Project Structure

```
mcp-notes/
├── mcp_notes/
│   ├── __init__.py
│   ├── __main__.py      # CLI entry point
│   ├── mcp_server.py    # FastMCP server and tools
│   └── storage.py       # Note storage management
├── tests/
├── pyproject.toml       # Project configuration
├── ruff.toml           # Linting configuration
└── README.md
```

## Requirements

- Python 3.8+
- FastMCP
- Model Context Protocol compatible client

## License

This project is available under the MIT License.