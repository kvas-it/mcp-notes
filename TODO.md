# List of tasks for the MCP Notes

MCP Notes is an MCP server for managing notes. It stores tagged and interlined
notes in a directory of markdown files and exposes tools to manage them. It's
written in Python using FastMCP.

## Tasks

- Add a tool to move notes between folders:
  - It should accept a note filename and a target folder.
  - Ensure the indexes are updated accordingly.
  - Update the links in existing notes to point to the new location:
    - Just seach existing notes for the old filename and replace it with the new
      one.

- Add tools to add and remove tags from notes:
  - `add_tags` tool to add new tags to a note:
    - Accepts note filename and a list of tags.
    - Update the tags in the note's text (first line under the title):
      - Load existing tags, parsem (split by comma), add new tags, regenerate
        the tags line, and write it back to the file.
    - Update the note's tags in the index.
  - `remove_tags` tool to remove tags from a note:
    - Accepts note filename and a list of tags to remove.
    - Load existing tags, parse them, remove specified tags, regenerate the
      tags line, and write it back to the file.
    - Update the note's tags in the index.

- Enhance indexes with subnote counts:
  - Add "children-count" key showing immediate subnotes
  - Add "descendant-count" key showing the count of all nested subnotes
    recursively.
  - Display counts in both main index and subfolder indexes.
  - Notes that don't have subnotes should not have these keys.
  - The counts in index files should be updated when notes are added or
    deleted.

- Implement automatic git commits for change tracking
  - Bundle related edits into logical commits (create, update, delete operations)
  - Add meaningful commit messages describing the changes
  - Consider batching multiple rapid edits into single commits with timeouts
  - Ensure git repository is initialized if not already present

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
