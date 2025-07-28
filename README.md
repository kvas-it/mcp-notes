# MCP Notes

MCP Notes is an MCP (Model Context Protocol) server for managing notes. It stores tagged notes in a directory of markdown files and exposes tools to manage them through the Model Context Protocol.

## Features

- **Add Notes**: Create new notes with titles, content, and tags
- **Hierarchical Structure**: Organize notes in a parent-child hierarchy with unlimited nesting levels
- **Retrieve Notes**: Get notes by filename, including nested notes
- **Update Notes**: Modify existing note content and tags by filename
- **List Notes**: View notes at any level of the hierarchy
- **Delete Notes**: Remove notes by filename with automatic cleanup of empty directories
- **Move Notes**: Relocate notes between directories with automatic reference updates
- **Tag Management**: Add and remove tags from existing notes
- **File-based Storage**: Notes are stored as markdown files in a hierarchical directory structure
- **JSON Index**: Fast lookups using separate JSON index files for each directory level
- **Automatic Counting**: Tracks children-count and descendant-count for notes with sub-notes

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
Create a new note with title, content, and optional tags. Can be nested under a parent note.
- `title` (str): Note title  
- `content` (str): Note content
- `tags` (List[str], optional): Tags for the note
- `parent` (str, optional): Parent note filename for hierarchical organization

#### `get_note`
Retrieve a note by filename, supporting nested paths.
- `filename` (str): Note filename (e.g., "note.md" or "parent/child.md")

#### `list_notes`
List notes at a specific hierarchy level. Returns note info including title, tags, and child counts.
- `parent` (str, optional): Parent directory to list children from (omit for top-level)

#### `update_note`
Update existing note content and tags while preserving the title.
- `filename` (str): Note filename to update
- `content` (str): New note content
- `tags` (List[str], optional): New tags for the note

#### `delete_note`
Delete a note by filename with automatic cleanup of empty directories.
- `filename` (str): Note filename to delete

#### `move_note`
Move a note to a different directory and update all references in other notes.
- `filename` (str): Note filename to move
- `target_folder` (str, optional): Target directory (None for root)

#### `add_tags`
Add new tags to an existing note, avoiding duplicates.
- `filename` (str): Note filename to add tags to
- `tags` (List[str]): Tags to add

#### `remove_tags`
Remove specified tags from an existing note.
- `filename` (str): Note filename to remove tags from  
- `tags` (List[str]): Tags to remove

**Example Usage:**
```python
# Create and organize notes
add_note(title="Project Alpha", content="Main project docs", tags=["project"])
add_note(title="Tasks", content="Task list", parent="project_alpha")

# Manage tags
add_tags(filename="project_alpha.md", tags=["urgent", "review"])
remove_tags(filename="project_alpha.md", tags=["review"])

# Move and reorganize
move_note(filename="project_alpha/tasks.md", target_folder="archive")
```

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

#### Count Information

For notes that have child notes, the index automatically includes count information:

```json
{
  "Project Alpha": {
    "filename": "project_alpha.md",
    "tags": ["work", "project"],
    "children-count": 3,
    "descendant-count": 8
  }
}
```

- **children-count**: Number of immediate child notes (direct children only)
- **descendant-count**: Total number of all nested notes recursively
- Notes without children do not have these keys to keep the index clean

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