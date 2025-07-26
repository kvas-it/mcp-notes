from typing import List
from pydantic import BaseModel
from fastmcp import FastMCP


class NoteInfo(BaseModel):
    filename: str
    title: str
    tags: List[str]


app = FastMCP(name='Notes')


@app.tool
def add_note(title: str, content: str, tags: List[str] = None) -> str:
    """Add a new note with title, content and tags."""
    if tags is None:
        tags = []

    note_path = app.storage.add_note(title, content, tags)
    return f"Note '{title}' created at {note_path.name}"


@app.tool
def get_note(filename: str) -> str:
    """Retrieve a note by filename."""
    content = app.storage.get_note(filename=filename)
    if content is None:
        raise ValueError(f"Note '{filename}' not found")

    return content


@app.tool
def list_notes() -> List[NoteInfo]:
    """List all notes."""
    notes_data = app.storage.list_notes()
    return [NoteInfo(**note) for note in notes_data]


@app.tool
def delete_note(filename: str) -> str:
    """Delete a note by filename."""
    success = app.storage.delete_note(filename=filename)
    if not success:
        raise ValueError(f"Note '{filename}' not found")

    return f"Note '{filename}' deleted"


@app.tool
def update_note(filename: str, content: str, tags: List[str] = None) -> str:
    """Update an existing note's content and tags by filename."""
    if tags is None:
        tags = []

    success = app.storage.update_note(filename=filename, content=content, tags=tags)
    if not success:
        raise ValueError(f"Note '{filename}' not found")

    return f"Note '{filename}' updated"
