# MCP Notes

MCP Notes is an MCP (Model Context Protocol) server for managing notes. It stores tagged notes in a directory of markdown files and exposes tools to manage them through the Model Context Protocol.

## Features

- **Add Notes**: Create new notes with titles, content, and tags
- **Hierarchical Structure**: Organize notes in a parent-child hierarchy with unlimited nesting levels
- **Retrieve Notes**: Get notes by filename, including nested notes
- **Update Notes**: Modify existing note content and tags by filename
- **List Notes**: View notes at any level of the hierarchy
- **Delete Notes**: Remove notes by filename with automatic cleanup of empty directories
- **Tag Support**: Organize notes with customizable tags
- **File-based Storage**: Notes are stored as markdown files in a hierarchical directory structure
- **JSON Index**: Fast lookups using separate JSON index files for each directory level

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
Add a new note with title, content, and optional tags. Can be created as a child of an existing note.

**Parameters:**
- `title` (str): The note title
- `content` (str): The note content
- `tags` (List[str], optional): List of tags for the note
- `parent` (str, optional): Parent note filename (with or without .md extension) to create a sub-note

**Examples:**
```python
# Create a top-level note
add_note(
    title="Project Alpha",
    content="Main project documentation",
    tags=["project", "work"]
)

# Create a child note under "Project Alpha"
add_note(
    title="Meeting Notes",
    content="Weekly standup discussions",
    tags=["meetings"],
    parent="project_alpha"  # or "project_alpha.md"
)
```

#### `get_note`
Retrieve a note by filename, including notes in subdirectories.

**Parameters:**
- `filename` (str): The note filename (e.g., "my_note.md" for top-level or "parent_name/child_note.md" for nested notes)

**Examples:**
```python
# Get a top-level note
get_note(filename="project_alpha.md")

# Get a nested note
get_note(filename="project_alpha/meeting_notes.md")
```

#### `list_notes`
List notes at a specific level of the hierarchy.

**Parameters:**
- `parent` (str, optional): Parent directory name to list child notes. If not provided, lists top-level notes only.

**Returns:** List of note information including filename, title, and tags.

**Examples:**
```python
# List all top-level notes
list_notes()

# List child notes under "project_alpha"
list_notes(parent="project_alpha")
```

#### `update_note`
Update an existing note's content and tags, including nested notes.

**Parameters:**
- `filename` (str): The note filename to update (e.g., "my_note.md" or "parent_name/child_note.md")
- `content` (str): The new note content
- `tags` (List[str], optional): New list of tags for the note

Note: The note's title will be preserved from the original note.

**Examples:**
```python
# Update a top-level note
update_note(
    filename="project_alpha.md",
    content="Updated project documentation",
    tags=["project", "work", "updated"]
)

# Update a nested note
update_note(
    filename="project_alpha/meeting_notes.md",
    content="Updated meeting notes with action items",
    tags=["meetings", "action-items"]
)
```

#### `delete_note`
Delete a note by filename. Empty parent directories are automatically cleaned up.

**Parameters:**
- `filename` (str): The note filename to delete (e.g., "my_note.md" or "parent_name/child_note.md")

## File Structure

### Hierarchical Organization

Notes are organized in a hierarchical directory structure:

```
notes_directory/
├── notes_index.json              # Index for top-level notes
├── project_alpha.md              # Top-level note
├── personal_notes.md             # Another top-level note
├── project_alpha/                # Subdirectory for project_alpha children
│   ├── notes_index.json          # Index for project_alpha children
│   ├── meeting_notes.md          # Child note
│   ├── tasks.md                  # Another child note
│   └── research/                 # Sub-subdirectory for deeper nesting
│       ├── notes_index.json      # Index for research notes
│       └── market_analysis.md    # Grandchild note
└── personal_notes/               # Subdirectory for personal_notes children
    ├── notes_index.json          # Index for personal_notes children
    └── shopping_list.md          # Child note
```

### Note Format

Each note is stored as a markdown file with the following format:

```markdown
# Note Title
Tags: tag1, tag2, tag3

Note content goes here...
```

### Index Files

Each directory maintains its own `notes_index.json` file for fast lookups within that level of the hierarchy. The index contains metadata for notes in that specific directory only, not for notes in subdirectories.

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