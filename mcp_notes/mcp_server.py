from typing import List, Optional
from pydantic import BaseModel
from fastmcp import FastMCP


class NoteInfo(BaseModel):
    filename: str
    title: str
    tags: List[str]
    children_count: Optional[int] = None
    descendant_count: Optional[int] = None


app = FastMCP(name='Notes')


@app.tool
def add_note(
    title: str, content: str, tags: List[str] = None, parent: str = None
) -> str:
    """Add a new note with title, content and tags.

    Creates a new note that can be either top-level or nested under a parent note.

    Args:
        title: The note title (used to generate filename)
        content: The note content in markdown format
        tags: Optional list of tags for categorizing the note
        parent: Optional parent note filename (with or without .md extension) to create a hierarchical sub-note.
                Examples: "project_alpha" or "project_alpha.md" or "project/subproject" for deep nesting

    Returns:
        Success message with the created note's filename

    Examples:
        - add_note("Project Alpha", "Main project notes", ["work", "project"])
          Creates: project_alpha.md
        - add_note("Meeting Notes", "Weekly standup", ["meetings"], parent="project_alpha")
          Creates: project_alpha/meeting_notes.md
        - add_note("Action Items", "Tasks", ["tasks"], parent="project_alpha/meeting_notes")
          Creates: project_alpha/meeting_notes/action_items.md
    """
    if tags is None:
        tags = []

    note_path = app.storage.add_note(title, content, tags, parent)
    return f"Note '{title}' created at {note_path.name}"


@app.tool
def get_note(filename: str) -> str:
    """Retrieve a note by filename, including hierarchical notes.

    Args:
        filename: The note filename to retrieve. Can be:
                 - Top-level: "my_note.md"
                 - Nested: "parent_name/child_note.md"
                 - Deep nested: "grandparent/parent/child.md"

    Returns:
        The complete note content including title, tags, and content

    Examples:
        - get_note("project_alpha.md") - retrieves top-level note
        - get_note("project_alpha/meeting_notes.md") - retrieves child note
        - get_note("project_alpha/research/market_analysis.md") - retrieves deeply nested note
    """
    content = app.storage.get_note(filename=filename)
    if content is None:
        raise ValueError(f"Note '{filename}' not found")

    return content


@app.tool
def list_notes(parent: str = None) -> List[NoteInfo]:
    """List notes at a specific level of the hierarchy.

    Args:
        parent: Optional parent directory name to list child notes from.
               If None, lists only top-level notes.
               Examples: "project_alpha", "project_alpha/research"

    Returns:
        List of NoteInfo objects containing filename, title, tags, and optional count information for notes at the specified level.
        Does NOT include notes from subdirectories - only direct children.
        Notes with children include children_count (immediate children) and descendant_count (all nested children).

    Examples:
        - list_notes() - returns ["project_alpha.md", "personal.md"] (top-level only)
        - list_notes(parent="project_alpha") - returns ["meeting_notes.md", "tasks.md"] (project_alpha children only)
        - list_notes(parent="project_alpha/research") - returns notes in the research subdirectory

    Note: To explore the full hierarchy, call list_notes() for top-level, then call list_notes(parent="...")
          for each parent you want to explore further.
    """
    notes_data = app.storage.list_notes(parent)
    return [NoteInfo(**note) for note in notes_data]


@app.tool
def delete_note(filename: str) -> str:
    """Delete a note by filename with automatic cleanup of empty directories.

    Args:
        filename: The note filename to delete. Can be:
                 - Top-level: "my_note.md"
                 - Nested: "parent_name/child_note.md"
                 - Deep nested: "grandparent/parent/child.md"

    Returns:
        Success message confirming deletion

    Behavior:
        - Deletes the specified note file
        - Removes the note from the appropriate index file
        - Automatically cleans up empty parent directories when the last child note is deleted

    Examples:
        - delete_note("project_alpha.md") - deletes top-level note
        - delete_note("project_alpha/meeting_notes.md") - deletes child note, may clean up project_alpha/ if empty
        - delete_note("project_alpha/research/market_analysis.md") - deletes deeply nested note
    """
    success = app.storage.delete_note(filename=filename)
    if not success:
        raise ValueError(f"Note '{filename}' not found")

    return f"Note '{filename}' deleted"


@app.tool
def update_note(filename: str, content: str, tags: List[str] = None) -> str:
    """Update an existing note's content and tags by filename.

    Args:
        filename: The note filename to update. Can be:
                 - Top-level: "my_note.md"
                 - Nested: "parent_name/child_note.md"
                 - Deep nested: "grandparent/parent/child.md"
        content: The new content for the note
        tags: Optional new list of tags (if not provided, existing tags are cleared)

    Returns:
        Success message confirming the update

    Behavior:
        - Updates the note file with new content and tags
        - Preserves the original note title
        - Updates the appropriate index file with new tag information

    Examples:
        - update_note("project_alpha.md", "Updated project description", ["project", "updated"])
        - update_note("project_alpha/meeting_notes.md", "New meeting content", ["meetings", "standup"])
        - update_note("project_alpha/research/market_analysis.md", "Detailed analysis", ["research", "analysis"])
    """
    if tags is None:
        tags = []

    success = app.storage.update_note(filename=filename, content=content, tags=tags)
    if not success:
        raise ValueError(f"Note '{filename}' not found")

    return f"Note '{filename}' updated"


@app.tool
def move_note(filename: str, target_folder: Optional[str] = None) -> str:
    """Move a note to a different folder and update all references.

    Args:
        filename: The note filename to move. Can be:
                 - Top-level: "my_note.md"
                 - Nested: "parent_name/child_note.md"
                 - Deep nested: "grandparent/parent/child.md"
        target_folder: Target folder name. Can be:
                      - None or empty string for root directory
                      - "folder_name" for moving to subfolder
                      - "parent/subfolder" for moving to nested folder

    Returns:
        Success message with the new filename after moving

    Behavior:
        - Moves the note file to the target location
        - Updates all index files appropriately
        - Updates parent/child counts automatically
        - Searches all existing notes for references to the old filename and replaces them with the new filename
        - Automatically cleans up empty directories when notes are moved out
        - Ensures unique filenames in the target directory

    Examples:
        - move_note("my_note.md", None) - moves to root directory
        - move_note("my_note.md", "projects") - moves to projects/ subfolder
        - move_note("projects/task.md", "archive") - moves from projects/ to archive/
        - move_note("projects/task.md", "projects/completed") - moves to nested subfolder
    """
    # Convert empty string to None for consistency
    if target_folder is not None and target_folder.strip() == '':
        target_folder = None

    new_filename = app.storage.move_note(filename=filename, target_folder=target_folder)

    target_desc = f"to '{target_folder}/'" if target_folder else 'to root directory'
    return f"Note '{filename}' moved {target_desc} as '{new_filename}'"


@app.tool
def add_tags(filename: str, tags: List[str]) -> str:
    """Add new tags to an existing note.

    Args:
        filename: The note filename to add tags to. Can be:
                 - Top-level: "my_note.md"
                 - Nested: "parent_name/child_note.md"
                 - Deep nested: "grandparent/parent/child.md"
        tags: List of tags to add to the note

    Returns:
        Success message confirming the tags were added

    Behavior:
        - Loads existing tags from the note
        - Adds new tags to the existing ones (avoiding duplicates)
        - Updates both the note file and the index
        - Preserves the note's title and content

    Examples:
        - add_tags("project.md", ["urgent", "review"]) - adds tags to top-level note
        - add_tags("project/task.md", ["completed"]) - adds tag to nested note
    """
    success = app.storage.add_tags(filename=filename, tags_to_add=tags)
    if not success:
        raise ValueError(f"Note '{filename}' not found")

    tags_str = ', '.join(tags)
    return f"Tags '{tags_str}' added to note '{filename}'"


@app.tool
def remove_tags(filename: str, tags: List[str]) -> str:
    """Remove specified tags from an existing note.

    Args:
        filename: The note filename to remove tags from. Can be:
                 - Top-level: "my_note.md"
                 - Nested: "parent_name/child_note.md"
                 - Deep nested: "grandparent/parent/child.md"
        tags: List of tags to remove from the note

    Returns:
        Success message confirming the tags were removed

    Behavior:
        - Loads existing tags from the note
        - Removes specified tags from the existing ones
        - Updates both the note file and the index
        - Preserves the note's title and content
        - Silently ignores tags that don't exist on the note

    Examples:
        - remove_tags("project.md", ["urgent"]) - removes tag from top-level note
        - remove_tags("project/task.md", ["draft", "review"]) - removes multiple tags from nested note
    """
    success = app.storage.remove_tags(filename=filename, tags_to_remove=tags)
    if not success:
        raise ValueError(f"Note '{filename}' not found")

    tags_str = ', '.join(tags)
    return f"Tags '{tags_str}' removed from note '{filename}'"
