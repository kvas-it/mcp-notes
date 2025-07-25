# List of tasks for the MCP Notes

MCP Notes is an MCP server for managing notes. It stores tagged and interlined
notes in a directory of markdown files and exposes tools to manage them. It's
written in Python using FastMCP.

## Tasks

- Set up CI using GitHub Actions
  - Run tests on master and on pull requests
  - Use the `venv` directory for the virtual environment
  - Run `ruff check` and `ruff format --check` on the codebase
  - Run tests using `pytest`
- Search in notes?
  - Can maybe request filtered index by tag?
  - What about full text search?
- Note hiearchy to make the main index smaller?
  - If we have many notes, the main index can become large. Since we don't have
    search and can only request the full list, this will take a lot of context.
  - One idea to fix it is to have a hierarchy of notes, where each note can
    reference other notes. Then we can have a main index that lists only the
    top-level notes, and each note can have its own index of sub-notes.
  - Then we can group notes by topic, generate a summary (potentially with
    links) and place all the notes of the topic under the topic. Only the root
    topic note will be visible in the main index, but the client can then
    request the root note and understand what it needs inside of it and where
    to find it. Or it can request the full list of subnotes of the topic and
    then decide which ones to load.

I don't think I understand how to implement the tasks above yet, so I will try
to get some experience with the MCP server first.
