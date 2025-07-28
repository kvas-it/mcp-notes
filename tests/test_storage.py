import json
import tempfile
from pathlib import Path

import pytest

from mcp_notes.storage import Storage


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def storage(temp_dir):
    return Storage(temp_dir)


def test_init(temp_dir):
    storage = Storage(temp_dir)
    assert storage.directory == temp_dir
    assert temp_dir.exists()


def test_add_note_basic(storage):
    title = 'My First Note'
    content = 'This is the content of my note.'
    tags = ['personal', 'first note']

    note_path = storage.add_note(title, content, tags)

    assert note_path.exists()
    assert note_path.name == 'my_first_note.md'

    # Check file content
    with open(note_path) as f:
        file_content = f.read()

    expected = (
        '# My First Note\nTags: personal, first note\n\nThis is the content of my note.'
    )
    assert file_content == expected


def test_add_note_special_chars(storage):
    title = 'Note with $pecial Ch@rs & Numb3rs!'
    content = 'Content'
    tags = []

    note_path = storage.add_note(title, content, tags)

    assert note_path.name == 'note_with_pecial_ch_rs_numb3rs.md'


def test_add_note_duplicate_names(storage):
    title = 'Duplicate'
    content1 = 'First'
    content2 = 'Second'

    path1 = storage.add_note(title, content1, [])
    path2 = storage.add_note(title, content2, [])

    assert path1.name == 'duplicate.md'
    assert path2.name == 'duplicate_1.md'


def test_add_note_updates_index(storage):
    title = 'Test Note'
    content = 'Content'
    tags = ['test']

    storage.add_note(title, content, tags)

    index_path = storage.directory / 'notes_index.json'
    assert index_path.exists()

    with open(index_path) as f:
        index = json.load(f)

    assert title in index
    assert index[title]['filename'] == 'test_note.md'
    assert index[title]['tags'] == tags


def test_get_note_by_filename(storage):
    title = 'Test Note'
    content = 'Test content'
    tags = ['test']

    storage.add_note(title, content, tags)
    result = storage.get_note(filename='test_note.md')

    expected = '# Test Note\nTags: test\n\nTest content'
    assert result == expected


def test_get_note_not_found(storage):
    result = storage.get_note(filename='non_existent.md')
    assert result is None


def test_list_notes_empty(storage):
    result = storage.list_notes()
    assert result == []


def test_list_notes(storage):
    storage.add_note('First Note', 'Content 1', ['tag1'])
    storage.add_note('Second Note', 'Content 2', ['tag2', 'tag3'])

    result = storage.list_notes()

    assert len(result) == 2

    # Sort by filename for consistent testing
    result.sort(key=lambda x: x['filename'])

    assert result[0]['filename'] == 'first_note.md'
    assert result[0]['title'] == 'First Note'
    assert result[0]['tags'] == ['tag1']

    assert result[1]['filename'] == 'second_note.md'
    assert result[1]['title'] == 'Second Note'
    assert result[1]['tags'] == ['tag2', 'tag3']


def test_delete_note_by_filename(storage):
    title = 'Test Note'
    storage.add_note(title, 'Content', ['test'])

    success = storage.delete_note(filename='test_note.md')
    assert success is True

    # Check file is gone
    note_path = storage.directory / 'test_note.md'
    assert not note_path.exists()

    # Check index is updated
    index_path = storage.directory / 'notes_index.json'
    with open(index_path) as f:
        index = json.load(f)
    assert title not in index


def test_delete_note_not_found(storage):
    success = storage.delete_note(filename='non_existent.md')
    assert success is False


def test_update_note_by_filename(storage):
    title = 'Test Note'
    storage.add_note(title, 'Original content', ['original'])

    success = storage.update_note(
        filename='test_note.md', content='Updated content', tags=['updated', 'tags']
    )
    assert success is True

    # Check file content is updated
    result = storage.get_note(filename='test_note.md')
    expected = '# Test Note\nTags: updated, tags\n\nUpdated content'
    assert result == expected

    # Check index is updated
    index_path = storage.directory / 'notes_index.json'
    with open(index_path) as f:
        index = json.load(f)
    assert index[title]['tags'] == ['updated', 'tags']


def test_update_note_empty_tags(storage):
    title = 'Test Note'
    storage.add_note(title, 'Original content', ['original'])

    success = storage.update_note(
        filename='test_note.md', content='Updated content', tags=[]
    )
    assert success is True

    result = storage.get_note(filename='test_note.md')
    expected = '# Test Note\nTags: \n\nUpdated content'
    assert result == expected


def test_update_note_not_found(storage):
    success = storage.update_note(
        filename='non_existent.md', content='Content', tags=[]
    )
    assert success is False


# Tests for hierarchical notes
def test_add_note_with_parent(storage):
    # Create parent note first
    parent_title = 'Parent Note'
    storage.add_note(parent_title, 'Parent content', ['parent'])

    # Create child note
    child_title = 'Child Note'
    child_path = storage.add_note(
        child_title, 'Child content', ['child'], parent='parent_note'
    )

    # Check that child note was created in subdirectory
    expected_child_path = storage.directory / 'parent_note' / 'child_note.md'
    assert child_path == expected_child_path
    assert child_path.exists()

    # Check that subdirectory was created
    parent_dir = storage.directory / 'parent_note'
    assert parent_dir.exists()
    assert parent_dir.is_dir()


def test_add_note_with_parent_md_extension(storage):
    # Create parent note first
    storage.add_note('Parent Note', 'Parent content', ['parent'])

    # Create child note using parent filename with .md extension
    child_path = storage.add_note(
        'Child Note', 'Child content', ['child'], parent='parent_note.md'
    )

    # Should work the same as without .md extension
    expected_child_path = storage.directory / 'parent_note' / 'child_note.md'
    assert child_path == expected_child_path
    assert child_path.exists()


def test_hierarchical_index_files(storage):
    # Create parent note
    storage.add_note('Parent Note', 'Parent content', ['parent'])

    # Create child note
    storage.add_note('Child Note', 'Child content', ['child'], parent='parent_note')

    # Check that main index only contains parent note
    main_index_path = storage.directory / 'notes_index.json'
    assert main_index_path.exists()

    with open(main_index_path) as f:
        main_index = json.load(f)

    assert 'Parent Note' in main_index
    assert 'Child Note' not in main_index  # Child should not be in main index

    # Check that child index exists and contains child note
    child_index_path = storage.directory / 'parent_note' / 'notes_index.json'
    assert child_index_path.exists()

    with open(child_index_path) as f:
        child_index = json.load(f)

    assert 'Child Note' in child_index
    assert child_index['Child Note']['filename'] == 'parent_note/child_note.md'


def test_get_note_hierarchical(storage):
    # Create parent and child notes
    storage.add_note('Parent Note', 'Parent content', ['parent'])
    storage.add_note('Child Note', 'Child content', ['child'], parent='parent_note')

    # Get child note using full path
    child_content = storage.get_note(filename='parent_note/child_note.md')

    expected = '# Child Note\nTags: child\n\nChild content'
    assert child_content == expected


def test_update_note_hierarchical(storage):
    # Create parent and child notes
    storage.add_note('Parent Note', 'Parent content', ['parent'])
    storage.add_note(
        'Child Note', 'Original content', ['original'], parent='parent_note'
    )

    # Update child note
    success = storage.update_note(
        filename='parent_note/child_note.md',
        content='Updated content',
        tags=['updated'],
    )
    assert success is True

    # Verify content was updated
    child_content = storage.get_note(filename='parent_note/child_note.md')
    expected = '# Child Note\nTags: updated\n\nUpdated content'
    assert child_content == expected


def test_delete_note_hierarchical(storage):
    # Create parent and child notes
    storage.add_note('Parent Note', 'Parent content', ['parent'])
    storage.add_note('Child Note', 'Child content', ['child'], parent='parent_note')

    # Delete child note
    success = storage.delete_note(filename='parent_note/child_note.md')
    assert success is True

    # Check that child note is gone
    child_path = storage.directory / 'parent_note' / 'child_note.md'
    assert not child_path.exists()

    # Check that child index is updated
    child_index_path = storage.directory / 'parent_note' / 'notes_index.json'
    if child_index_path.exists():
        with open(child_index_path) as f:
            child_index = json.load(f)
        assert 'Child Note' not in child_index


def test_directory_cleanup_on_last_note_deletion(storage):
    # Create parent and child notes
    storage.add_note('Parent Note', 'Parent content', ['parent'])
    storage.add_note('Child Note', 'Child content', ['child'], parent='parent_note')

    parent_dir = storage.directory / 'parent_note'
    assert parent_dir.exists()

    # Delete the only child note
    storage.delete_note(filename='parent_note/child_note.md')

    # Directory should be cleaned up since it's empty
    assert not parent_dir.exists()


def test_list_notes_hierarchical(storage):
    # Create parent and child notes
    storage.add_note('Parent Note', 'Parent content', ['parent'])
    storage.add_note(
        'Child Note 1', 'Child content 1', ['child1'], parent='parent_note'
    )
    storage.add_note(
        'Child Note 2', 'Child content 2', ['child2'], parent='parent_note'
    )

    # List top-level notes (should only show parent)
    top_notes = storage.list_notes()
    assert len(top_notes) == 1
    assert top_notes[0]['title'] == 'Parent Note'

    # List notes in parent directory (should show children)
    child_notes = storage.list_notes(parent='parent_note')
    assert len(child_notes) == 2

    child_titles = {note['title'] for note in child_notes}
    assert child_titles == {'Child Note 1', 'Child Note 2'}


def test_multiple_levels_nesting(storage):
    # Create three levels of notes
    storage.add_note('Grandparent', 'Grandparent content', ['gp'])
    storage.add_note('Parent', 'Parent content', ['p'], parent='grandparent')
    storage.add_note('Child', 'Child content', ['c'], parent='grandparent/parent')

    # Check that all levels exist
    grandparent_path = storage.directory / 'grandparent.md'
    parent_path = storage.directory / 'grandparent' / 'parent.md'
    child_path = storage.directory / 'grandparent' / 'parent' / 'child.md'

    assert grandparent_path.exists()
    assert parent_path.exists()
    assert child_path.exists()

    # Check that we can retrieve the deeply nested child
    child_content = storage.get_note(filename='grandparent/parent/child.md')
    expected = '# Child\nTags: c\n\nChild content'
    assert child_content == expected


def test_unique_filenames_in_subdirectories(storage):
    # Create parent note
    storage.add_note('Parent Note', 'Parent content', ['parent'])

    # Create two child notes with same title
    child_path_1 = storage.add_note(
        'Duplicate', 'First child', ['child1'], parent='parent_note'
    )
    child_path_2 = storage.add_note(
        'Duplicate', 'Second child', ['child2'], parent='parent_note'
    )

    # Should have different filenames
    assert child_path_1.name == 'duplicate.md'
    assert child_path_2.name == 'duplicate_1.md'

    # Both should exist in the same parent directory
    parent_dir = storage.directory / 'parent_note'
    assert (parent_dir / 'duplicate.md').exists()
    assert (parent_dir / 'duplicate_1.md').exists()


# Tests for count functionality
def test_children_count_basic(storage):
    # Create parent note
    storage.add_note('Parent Note', 'Parent content', ['parent'])

    # Initially should have no count keys (no children)
    notes = storage.list_notes()
    parent_note = next(note for note in notes if note['title'] == 'Parent Note')
    assert 'children_count' not in parent_note
    assert 'descendant_count' not in parent_note

    # Add child note
    storage.add_note('Child Note', 'Child content', ['child'], parent='parent_note')

    # Now should have count information
    notes = storage.list_notes()
    parent_note = next(note for note in notes if note['title'] == 'Parent Note')
    assert parent_note['children_count'] == 1
    assert parent_note['descendant_count'] == 1


def test_children_count_multiple_children(storage):
    # Create parent note
    storage.add_note('Project', 'Project description', ['project'])

    # Add multiple children
    storage.add_note('Task 1', 'First task', ['task'], parent='project')
    storage.add_note('Task 2', 'Second task', ['task'], parent='project')
    storage.add_note('Meeting Notes', 'Meeting content', ['meeting'], parent='project')

    # Check counts
    notes = storage.list_notes()
    parent_note = next(note for note in notes if note['title'] == 'Project')
    assert parent_note['children_count'] == 3
    assert parent_note['descendant_count'] == 3


def test_descendant_count_nested_hierarchy(storage):
    # Create three levels: grandparent -> parent -> child
    storage.add_note('Grandparent', 'GP content', ['gp'])
    storage.add_note('Parent', 'P content', ['p'], parent='grandparent')
    storage.add_note('Child', 'C content', ['c'], parent='grandparent/parent')

    # Check grandparent counts (should include all descendants)
    notes = storage.list_notes()
    grandparent_note = next(note for note in notes if note['title'] == 'Grandparent')
    assert grandparent_note['children_count'] == 1  # Only immediate children
    assert grandparent_note['descendant_count'] == 2  # All descendants

    # Check parent counts
    parent_notes = storage.list_notes(parent='grandparent')
    parent_note = next(note for note in parent_notes if note['title'] == 'Parent')
    assert parent_note['children_count'] == 1
    assert parent_note['descendant_count'] == 1


def test_count_updates_on_deletion(storage):
    # Create parent with children
    storage.add_note('Project', 'Project content', ['project'])
    storage.add_note('Task 1', 'Task 1 content', ['task'], parent='project')
    storage.add_note('Task 2', 'Task 2 content', ['task'], parent='project')

    # Verify initial counts
    notes = storage.list_notes()
    parent_note = next(note for note in notes if note['title'] == 'Project')
    assert parent_note['children_count'] == 2
    assert parent_note['descendant_count'] == 2

    # Delete one child
    storage.delete_note(filename='project/task_1.md')

    # Verify updated counts
    notes = storage.list_notes()
    parent_note = next(note for note in notes if note['title'] == 'Project')
    assert parent_note['children_count'] == 1
    assert parent_note['descendant_count'] == 1

    # Delete last child
    storage.delete_note(filename='project/task_2.md')

    # Verify counts are removed (no children)
    notes = storage.list_notes()
    parent_note = next(note for note in notes if note['title'] == 'Project')
    assert 'children_count' not in parent_note
    assert 'descendant_count' not in parent_note


def test_count_complex_hierarchy(storage):
    # Create a complex hierarchy
    # Root -> Branch1 -> Leaf1
    #      -> Branch2 -> Leaf2
    #                 -> Leaf3
    storage.add_note('Root', 'Root content', ['root'])
    storage.add_note('Branch 1', 'Branch 1 content', ['branch'], parent='root')
    storage.add_note('Branch 2', 'Branch 2 content', ['branch'], parent='root')
    storage.add_note('Leaf 1', 'Leaf 1 content', ['leaf'], parent='root/branch_1')
    storage.add_note('Leaf 2', 'Leaf 2 content', ['leaf'], parent='root/branch_2')
    storage.add_note('Leaf 3', 'Leaf 3 content', ['leaf'], parent='root/branch_2')

    # Check root counts
    notes = storage.list_notes()
    root_note = next(note for note in notes if note['title'] == 'Root')
    assert root_note['children_count'] == 2  # Branch 1, Branch 2
    assert (
        root_note['descendant_count'] == 5
    )  # Branch 1, Branch 2, Leaf 1, Leaf 2, Leaf 3

    # Check branch 1 counts
    branch_notes = storage.list_notes(parent='root')
    branch1_note = next(note for note in branch_notes if note['title'] == 'Branch 1')
    assert branch1_note['children_count'] == 1  # Leaf 1
    assert branch1_note['descendant_count'] == 1  # Leaf 1

    # Check branch 2 counts
    branch2_note = next(note for note in branch_notes if note['title'] == 'Branch 2')
    assert branch2_note['children_count'] == 2  # Leaf 2, Leaf 3
    assert branch2_note['descendant_count'] == 2  # Leaf 2, Leaf 3


def test_count_persistence_in_index_files(storage):
    # Create hierarchy
    storage.add_note('Project', 'Project content', ['project'])
    storage.add_note('Task', 'Task content', ['task'], parent='project')

    # Check that counts are persisted in the index file
    main_index_path = storage.directory / 'notes_index.json'
    with open(main_index_path) as f:
        main_index = json.load(f)

    project_data = main_index['Project']
    assert project_data['children-count'] == 1
    assert project_data['descendant-count'] == 1

    # Child notes should not have count keys (no children)
    child_index_path = storage.directory / 'project' / 'notes_index.json'
    with open(child_index_path) as f:
        child_index = json.load(f)

    task_data = child_index['Task']
    assert 'children-count' not in task_data
    assert 'descendant-count' not in task_data


def test_count_with_existing_notes_migration(storage):
    # Test that adding new notes to existing hierarchy updates all counts correctly
    # Create parent note normally
    storage.add_note('Existing Parent', 'Existing content', ['old'])

    # Verify no counts initially
    notes = storage.list_notes()
    parent_note = next(note for note in notes if note['title'] == 'Existing Parent')
    assert 'children_count' not in parent_note

    # Now add a child note - this should trigger count updates
    storage.add_note(
        'Existing Child', 'Child content', ['old'], parent='existing_parent'
    )

    # Now should have count information
    notes = storage.list_notes()
    parent_note = next(note for note in notes if note['title'] == 'Existing Parent')

    # Should now have count information
    assert parent_note['children_count'] == 1
    assert parent_note['descendant_count'] == 1


# Tests for move_note functionality
def test_move_note_to_root(storage):
    """Test moving a note from subfolder to root directory."""
    # Create parent and child notes
    storage.add_note('Parent Note', 'Parent content', ['parent'])
    storage.add_note('Child Note', 'Child content', ['child'], parent='parent_note')

    # Move child to root
    new_filename = storage.move_note(
        filename='parent_note/child_note.md', target_folder=None
    )

    # Check new filename
    assert new_filename == 'child_note.md'

    # Check that note exists in new location
    root_content = storage.get_note(filename='child_note.md')
    expected = '# Child Note\nTags: child\n\nChild content'
    assert root_content == expected

    # Check that note no longer exists in old location
    old_content = storage.get_note(filename='parent_note/child_note.md')
    assert old_content is None

    # Check indexes are updated
    root_notes = storage.list_notes()
    child_titles = {note['title'] for note in root_notes}
    assert 'Child Note' in child_titles

    parent_notes = storage.list_notes(parent='parent_note')
    child_titles_in_parent = {note['title'] for note in parent_notes}
    assert 'Child Note' not in child_titles_in_parent


def test_move_note_to_subfolder(storage):
    """Test moving a note from root to subfolder."""
    # Create notes
    storage.add_note('Root Note', 'Root content', ['root'])
    storage.add_note('Archive Folder', 'Archive content', ['archive'])

    # Move root note to archive folder
    new_filename = storage.move_note(
        filename='root_note.md', target_folder='archive_folder'
    )

    # Check new filename
    assert new_filename == 'archive_folder/root_note.md'

    # Check that note exists in new location
    moved_content = storage.get_note(filename='archive_folder/root_note.md')
    expected = '# Root Note\nTags: root\n\nRoot content'
    assert moved_content == expected

    # Check that note no longer exists in old location
    old_content = storage.get_note(filename='root_note.md')
    assert old_content is None

    # Check indexes are updated
    root_notes = storage.list_notes()
    root_titles = {note['title'] for note in root_notes}
    assert 'Root Note' not in root_titles

    archive_notes = storage.list_notes(parent='archive_folder')
    archive_titles = {note['title'] for note in archive_notes}
    assert 'Root Note' in archive_titles


def test_move_note_between_subfolders(storage):
    """Test moving a note from one subfolder to another."""
    # Create folder structure
    storage.add_note('Folder A', 'Folder A content', ['folderA'])
    storage.add_note('Folder B', 'Folder B content', ['folderB'])
    storage.add_note('Task', 'Task content', ['task'], parent='folder_a')

    # Move task from folder A to folder B
    new_filename = storage.move_note(
        filename='folder_a/task.md', target_folder='folder_b'
    )

    # Check new filename
    assert new_filename == 'folder_b/task.md'

    # Check that note exists in new location
    moved_content = storage.get_note(filename='folder_b/task.md')
    expected = '# Task\nTags: task\n\nTask content'
    assert moved_content == expected

    # Check that note no longer exists in old location
    old_content = storage.get_note(filename='folder_a/task.md')
    assert old_content is None

    # Check indexes are updated
    folder_a_notes = storage.list_notes(parent='folder_a')
    folder_a_titles = {note['title'] for note in folder_a_notes}
    assert 'Task' not in folder_a_titles

    folder_b_notes = storage.list_notes(parent='folder_b')
    folder_b_titles = {note['title'] for note in folder_b_notes}
    assert 'Task' in folder_b_titles


def test_move_note_to_nested_folder(storage):
    """Test moving a note to a deeply nested folder."""
    # Create structure
    storage.add_note('Project', 'Project content', ['project'])
    storage.add_note('Archive', 'Archive content', ['archive'], parent='project')
    storage.add_note('Task', 'Task content', ['task'])

    # Move task to nested location
    new_filename = storage.move_note(
        filename='task.md', target_folder='project/archive'
    )

    # Check new filename
    assert new_filename == 'project/archive/task.md'

    # Check that note exists in new location
    moved_content = storage.get_note(filename='project/archive/task.md')
    expected = '# Task\nTags: task\n\nTask content'
    assert moved_content == expected

    # Check that nested index is updated
    nested_notes = storage.list_notes(parent='project/archive')
    nested_titles = {note['title'] for note in nested_notes}
    assert 'Task' in nested_titles


def test_move_note_updates_references(storage):
    """Test that moving a note updates references in other notes."""
    # Create notes with references
    storage.add_note('Main', 'See also task.md for details', ['main'])
    storage.add_note('Other', 'Related to task.md', ['other'])
    storage.add_note('Task', 'Task content', ['task'])
    storage.add_note('Archive', 'Archive content', ['archive'])

    # Move task to archive folder
    storage.move_note(filename='task.md', target_folder='archive')

    # Check that references were updated
    main_content = storage.get_note(filename='main.md')
    assert 'archive/task.md' in main_content
    assert 'task.md' not in main_content.replace('archive/task.md', '')

    other_content = storage.get_note(filename='other.md')
    assert 'archive/task.md' in other_content
    assert 'task.md' not in other_content.replace('archive/task.md', '')


def test_move_note_handles_duplicate_names(storage):
    """Test that moving a note handles duplicate names in target folder."""
    # Create notes with same title in different locations
    storage.add_note('Task A', 'Root task', ['root'])
    storage.add_note('Archive', 'Archive content', ['archive'])
    storage.add_note('Task B', 'Archive task', ['archived'], parent='archive')

    # Move root task to archive (should get unique name)
    new_filename = storage.move_note(filename='task_a.md', target_folder='archive')

    # Should get unique filename based on title
    assert new_filename == 'archive/task_a.md'

    # Both tasks should exist in archive
    archive_notes = storage.list_notes(parent='archive')
    assert len(archive_notes) == 2

    archive_titles = {note['title'] for note in archive_notes}
    assert 'Task A' in archive_titles  # Moved task
    assert 'Task B' in archive_titles  # Original archive task


def test_move_note_updates_parent_counts(storage):
    """Test that moving notes updates parent children/descendant counts."""
    # Create hierarchy
    storage.add_note('Project A', 'Project A content', ['projectA'])
    storage.add_note('Project B', 'Project B content', ['projectB'])
    storage.add_note('Task 1', 'Task 1 content', ['task'], parent='project_a')
    storage.add_note('Task 2', 'Task 2 content', ['task'], parent='project_a')

    # Check initial counts
    root_notes = storage.list_notes()
    project_a = next(note for note in root_notes if note['title'] == 'Project A')
    project_b = next(note for note in root_notes if note['title'] == 'Project B')

    assert project_a['children_count'] == 2
    assert project_a['descendant_count'] == 2
    assert 'children_count' not in project_b  # No children yet

    # Move one task from A to B
    storage.move_note(filename='project_a/task_1.md', target_folder='project_b')

    # Check updated counts
    root_notes = storage.list_notes()
    project_a = next(note for note in root_notes if note['title'] == 'Project A')
    project_b = next(note for note in root_notes if note['title'] == 'Project B')

    assert project_a['children_count'] == 1
    assert project_a['descendant_count'] == 1
    assert project_b['children_count'] == 1
    assert project_b['descendant_count'] == 1


def test_move_note_cleans_up_empty_directories(storage):
    """Test that moving the last note from a folder cleans up the empty directory."""
    # Create hierarchy
    storage.add_note('Project', 'Project content', ['project'])
    storage.add_note('Only Task', 'Only task content', ['task'], parent='project')

    project_dir = storage.directory / 'project'
    assert project_dir.exists()

    # Move the only task to root
    storage.move_note(filename='project/only_task.md', target_folder=None)

    # Directory should be cleaned up
    assert not project_dir.exists()


def test_move_note_no_op_same_location(storage):
    """Test that moving a note to its current location is a no-op."""
    # Create note
    storage.add_note('Task', 'Task content', ['task'])

    # Try to move to same location
    new_filename = storage.move_note(filename='task.md', target_folder=None)

    # Should return same filename
    assert new_filename == 'task.md'

    # Note should still exist and be unchanged
    content = storage.get_note(filename='task.md')
    expected = '# Task\nTags: task\n\nTask content'
    assert content == expected


def test_move_note_nonexistent_source(storage):
    """Test that moving a nonexistent note raises an error."""
    with pytest.raises(ValueError, match="Source note 'nonexistent.md' not found"):
        storage.move_note(filename='nonexistent.md', target_folder='archive')


def test_move_note_preserves_title_and_tags(storage):
    """Test that moving a note preserves the original title and tags."""
    # Create note with specific title and tags
    storage.add_note(
        'Complex Title with Special Characters!',
        'Content here',
        ['tag1', 'tag2', 'tag3'],
    )
    storage.add_note('Archive', 'Archive content', ['archive'])

    # Move to archive
    new_filename = storage.move_note(
        filename='complex_title_with_special_characters.md', target_folder='archive'
    )

    # Check that title and tags are preserved
    moved_content = storage.get_note(filename=new_filename)
    assert moved_content.startswith('# Complex Title with Special Characters!')
    assert 'Tags: tag1, tag2, tag3' in moved_content
    assert 'Content here' in moved_content

    # Check that index has correct metadata
    archive_notes = storage.list_notes(parent='archive')
    moved_note = next(
        note
        for note in archive_notes
        if note['title'] == 'Complex Title with Special Characters!'
    )
    assert moved_note['tags'] == ['tag1', 'tag2', 'tag3']


def test_move_note_deep_nesting(storage):
    """Test moving notes in deeply nested hierarchies."""
    # Create deep hierarchy
    storage.add_note('Level 1', 'L1 content', ['l1'])
    storage.add_note('Level 2', 'L2 content', ['l2'], parent='level_1')
    storage.add_note('Level 3', 'L3 content', ['l3'], parent='level_1/level_2')
    storage.add_note('Task', 'Task content', ['task'], parent='level_1/level_2/level_3')

    # Move deeply nested task to root
    new_filename = storage.move_note(
        filename='level_1/level_2/level_3/task.md', target_folder=None
    )

    # Check new location
    assert new_filename == 'task.md'
    root_content = storage.get_note(filename='task.md')
    expected = '# Task\nTags: task\n\nTask content'
    assert root_content == expected

    # Check old location is gone
    old_content = storage.get_note(filename='level_1/level_2/level_3/task.md')
    assert old_content is None


# Tests for tag management functionality
def test_add_tags_basic(storage):
    """Test adding tags to a note."""
    # Create a note with initial tags
    storage.add_note('Test Note', 'Test content', ['initial', 'tag'])

    # Add new tags
    success = storage.add_tags(filename='test_note.md', tags_to_add=['new', 'added'])
    assert success is True

    # Check file content is updated
    content = storage.get_note(filename='test_note.md')
    assert 'Tags: added, initial, new, tag' in content

    # Check index is updated
    notes = storage.list_notes()
    test_note = next(note for note in notes if note['title'] == 'Test Note')
    assert set(test_note['tags']) == {'initial', 'tag', 'new', 'added'}


def test_add_tags_avoids_duplicates(storage):
    """Test that adding existing tags doesn't create duplicates."""
    # Create a note with initial tags
    storage.add_note('Test Note', 'Test content', ['existing', 'tag'])

    # Try to add tags, including one that already exists
    success = storage.add_tags(filename='test_note.md', tags_to_add=['existing', 'new'])
    assert success is True

    # Check that duplicates are avoided
    content = storage.get_note(filename='test_note.md')
    assert content.count('existing') == 1

    # Check index has unique tags
    notes = storage.list_notes()
    test_note = next(note for note in notes if note['title'] == 'Test Note')
    assert set(test_note['tags']) == {'existing', 'tag', 'new'}


def test_add_tags_to_empty_tags(storage):
    """Test adding tags to a note that has no existing tags."""
    # Create a note with no tags
    storage.add_note('Empty Tags Note', 'Test content', [])

    # Add tags
    success = storage.add_tags(
        filename='empty_tags_note.md', tags_to_add=['first', 'second']
    )
    assert success is True

    # Check file content is updated
    content = storage.get_note(filename='empty_tags_note.md')
    assert 'Tags: first, second' in content

    # Check index is updated
    notes = storage.list_notes()
    test_note = next(note for note in notes if note['title'] == 'Empty Tags Note')
    assert set(test_note['tags']) == {'first', 'second'}


def test_add_tags_not_found(storage):
    """Test adding tags to a non-existent note."""
    success = storage.add_tags(filename='non_existent.md', tags_to_add=['tag'])
    assert success is False


def test_add_tags_hierarchical(storage):
    """Test adding tags to hierarchical notes."""
    # Create parent and child notes
    storage.add_note('Parent Note', 'Parent content', ['parent'])
    storage.add_note('Child Note', 'Child content', ['child'], parent='parent_note')

    # Add tags to child note
    success = storage.add_tags(
        filename='parent_note/child_note.md', tags_to_add=['new', 'tags']
    )
    assert success is True

    # Check child note content
    content = storage.get_note(filename='parent_note/child_note.md')
    assert 'Tags: child, new, tags' in content

    # Check child index is updated
    child_notes = storage.list_notes(parent='parent_note')
    child_note = next(note for note in child_notes if note['title'] == 'Child Note')
    assert set(child_note['tags']) == {'child', 'new', 'tags'}


def test_remove_tags_basic(storage):
    """Test removing tags from a note."""
    # Create a note with multiple tags
    storage.add_note('Test Note', 'Test content', ['tag1', 'tag2', 'tag3', 'tag4'])

    # Remove some tags
    success = storage.remove_tags(
        filename='test_note.md', tags_to_remove=['tag2', 'tag4']
    )
    assert success is True

    # Check file content is updated
    content = storage.get_note(filename='test_note.md')
    assert 'Tags: tag1, tag3' in content

    # Check index is updated
    notes = storage.list_notes()
    test_note = next(note for note in notes if note['title'] == 'Test Note')
    assert set(test_note['tags']) == {'tag1', 'tag3'}


def test_remove_tags_nonexistent(storage):
    """Test removing tags that don't exist on the note."""
    # Create a note with some tags
    storage.add_note('Test Note', 'Test content', ['existing', 'tag'])

    # Try to remove tags that don't exist
    success = storage.remove_tags(
        filename='test_note.md', tags_to_remove=['nonexistent', 'missing']
    )
    assert success is True

    # Check that existing tags are unchanged
    content = storage.get_note(filename='test_note.md')
    assert 'Tags: existing, tag' in content

    # Check index is unchanged
    notes = storage.list_notes()
    test_note = next(note for note in notes if note['title'] == 'Test Note')
    assert set(test_note['tags']) == {'existing', 'tag'}


def test_remove_tags_all(storage):
    """Test removing all tags from a note."""
    # Create a note with tags
    storage.add_note('Test Note', 'Test content', ['tag1', 'tag2'])

    # Remove all tags
    success = storage.remove_tags(
        filename='test_note.md', tags_to_remove=['tag1', 'tag2']
    )
    assert success is True

    # Check file content has empty tags
    content = storage.get_note(filename='test_note.md')
    assert 'Tags: \n\n' in content

    # Check index has empty tags
    notes = storage.list_notes()
    test_note = next(note for note in notes if note['title'] == 'Test Note')
    assert test_note['tags'] == []


def test_remove_tags_not_found(storage):
    """Test removing tags from a non-existent note."""
    success = storage.remove_tags(filename='non_existent.md', tags_to_remove=['tag'])
    assert success is False


def test_remove_tags_hierarchical(storage):
    """Test removing tags from hierarchical notes."""
    # Create parent and child notes
    storage.add_note('Parent Note', 'Parent content', ['parent'])
    storage.add_note(
        'Child Note',
        'Child content',
        ['child', 'draft', 'review'],
        parent='parent_note',
    )

    # Remove tags from child note
    success = storage.remove_tags(
        filename='parent_note/child_note.md', tags_to_remove=['draft', 'review']
    )
    assert success is True

    # Check child note content
    content = storage.get_note(filename='parent_note/child_note.md')
    assert 'Tags: child\n\n' in content

    # Check child index is updated
    child_notes = storage.list_notes(parent='parent_note')
    child_note = next(note for note in child_notes if note['title'] == 'Child Note')
    assert child_note['tags'] == ['child']


def test_tag_operations_preserve_content(storage):
    """Test that tag operations preserve note title and content."""
    original_title = 'Complex Title with Special Characters!'
    original_content = (
        'This is some complex content\nwith multiple lines\n\nand empty lines.'
    )

    # Create note
    storage.add_note(original_title, original_content, ['initial'])

    # Add tags
    storage.add_tags(
        filename='complex_title_with_special_characters.md', tags_to_add=['added']
    )

    # Remove tags
    storage.remove_tags(
        filename='complex_title_with_special_characters.md', tags_to_remove=['initial']
    )

    # Check that title and content are preserved
    final_content = storage.get_note(
        filename='complex_title_with_special_characters.md'
    )
    assert f'# {original_title}' in final_content
    assert original_content in final_content
    assert 'Tags: added' in final_content
