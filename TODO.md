# List of tasks for the MCP Notes

MCP Notes is an MCP server for managing notes. It stores tagged and interlined
notes in a directory of markdown files and exposes tools to manage them. It's
written in Python using FastMCP.

## Tasks

- Set up version control:
  - Initialize a Git repository in the project root.
  - Create a `.gitignore` file to exclude unnecessary files:
    - Exclude `__pycache__`, `.pytest_cache`, and other temporary files.
    - Include `venv/` to ignore the virtual environment directory.
  - Commit the initial project structure and files.
- Add methods to the `Storage` class:
  - Implement `add_note` method to create a new note file with a given title,
    content and tags.
    - It should return the path to the created note file.
    - Derive the file name from the title, replacing spaces with underscores
      and lowering the case (ensure unique file names).
    - Keep an index of all notes (title -> {filename, tags}) in a JSON file.
    - The content of the note should be in markdown format. At the top, first
      level title containing the note title, followed by comma-separated tags
      in one line (`Tags: tag1, tag two, tag/three`) and then an empty line,
      followed by the note content.
  - Implement `get_note` method to retrieve a note by title or filename (use
    keyword args, return markdown content).
  - Implement `list_notes` method to list all notes in the directory. It should
    return a list of dicts {filename, title, tags}.
  - Implement `delete_note` method to delete a note by title or filename (use
    keyword args). It should remove the note file and update the index.
- 
- Create a `README.md` file with project description.
