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
