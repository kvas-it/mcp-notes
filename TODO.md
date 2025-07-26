# List of tasks for the MCP Notes

MCP Notes is an MCP server for managing notes. It stores tagged and interlined
notes in a directory of markdown files and exposes tools to manage them. It's
written in Python using FastMCP.

## Tasks

- Implement hierarchical notes with parent/child relationships
  - Allow creating notes under another note by passing the parent note filename
    in `parent` parameter in `add_note` (wither with or without `.md` extension
    should be accepted)
  - Sub-notes should be stored in subfolders (e.g.,
    `parent_name/child_name.md`). Here we create a folder whose name is the
    same as parent filename but without `.md` extension. So the parent note
    is still in `parent_name.md` file, and there's a folder `parent_name` next
    to it containing the child note `child_name.md`.
  - Child notes should be accessible (for get_note, update_note, delete_note)
    via filename `parent_name/child_name.md`.
  - Each subfolder should maintain its own index.json file that lists
    the notes in that subfolder. The format of the index should be as before,
    the index listing the notes in the same folder as the index file (but not
    in subfolders).
  - Support multiple levels of nesting (parent/child/grandchild). The logic
    for sub-sub-notes is the same as for sub-notes.

- Listing notes in subfolders
  - `list_notes` should support an optional `parent` parameter to list
    notes in a specific subfolder (e.g., `parent_name/`).
  - `list_notes` without `parent` returns only top-level notes in the
    main index. `list_notes` with `parent` returns notes in that folder (or
    under that parent note), but not deeper ones.

- Enhance indexes with subnote counts:
  - Add "children-count" key showing immediate subnotes
  - Add "descendant-count" key showing the count of all nested subnotes
    recursively.
  - Display counts in both main index and subfolder indexes.
  - Notes that don't have subnotes should not have these keys.
  - The counts in index files should be updated when notes are added or
    deleted.

- When 

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
