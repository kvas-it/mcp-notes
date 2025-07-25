from typing import List, Optional
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
def get_note(title: Optional[str] = None, filename: Optional[str] = None) -> str:
    """Retrieve a note by title or filename."""
    if not title and not filename:
        raise ValueError('Must provide either title or filename')

    content = app.storage.get_note(title=title, filename=filename)
    if content is None:
        identifier = title or filename
        raise ValueError(f"Note '{identifier}' not found")

    return content


@app.tool
def list_notes() -> List[NoteInfo]:
    """List all notes."""
    notes_data = app.storage.list_notes()
    return [NoteInfo(**note) for note in notes_data]


@app.tool
def delete_note(title: Optional[str] = None, filename: Optional[str] = None) -> str:
    """Delete a note by title or filename."""
    if not title and not filename:
        raise ValueError('Must provide either title or filename')

    success = app.storage.delete_note(title=title, filename=filename)
    if not success:
        identifier = title or filename
        raise ValueError(f"Note '{identifier}' not found")

    identifier = title or filename
    return f"Note '{identifier}' deleted"
