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


def test_get_note_by_title(storage):
    title = 'Test Note'
    content = 'Test content'
    tags = ['test']

    storage.add_note(title, content, tags)
    result = storage.get_note(title=title)

    expected = '# Test Note\nTags: test\n\nTest content'
    assert result == expected


def test_get_note_by_filename(storage):
    title = 'Test Note'
    content = 'Test content'
    tags = ['test']

    storage.add_note(title, content, tags)
    result = storage.get_note(filename='test_note.md')

    expected = '# Test Note\nTags: test\n\nTest content'
    assert result == expected


def test_get_note_not_found(storage):
    result = storage.get_note(title='Non-existent')
    assert result is None

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


def test_delete_note_by_title(storage):
    title = 'Test Note'
    storage.add_note(title, 'Content', ['test'])

    success = storage.delete_note(title=title)
    assert success is True

    # Check file is gone
    note_path = storage.directory / 'test_note.md'
    assert not note_path.exists()

    # Check index is updated
    index_path = storage.directory / 'notes_index.json'
    with open(index_path) as f:
        index = json.load(f)
    assert title not in index


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
    success = storage.delete_note(title='Non-existent')
    assert success is False

    success = storage.delete_note(filename='non_existent.md')
    assert success is False


def test_update_note_by_title(storage):
    title = 'Test Note'
    storage.add_note(title, 'Original content', ['original'])

    success = storage.update_note(
        title=title, content='Updated content', tags=['updated', 'tags']
    )
    assert success is True

    # Check file content is updated
    result = storage.get_note(title=title)
    expected = '# Test Note\nTags: updated, tags\n\nUpdated content'
    assert result == expected

    # Check index is updated
    index_path = storage.directory / 'notes_index.json'
    with open(index_path) as f:
        index = json.load(f)
    assert index[title]['tags'] == ['updated', 'tags']


def test_update_note_by_filename(storage):
    title = 'Test Note'
    storage.add_note(title, 'Original content', ['original'])

    success = storage.update_note(
        filename='test_note.md', content='Updated content', tags=['updated']
    )
    assert success is True

    # Check file content is updated
    result = storage.get_note(filename='test_note.md')
    expected = '# Test Note\nTags: updated\n\nUpdated content'
    assert result == expected


def test_update_note_empty_tags(storage):
    title = 'Test Note'
    storage.add_note(title, 'Original content', ['original'])

    success = storage.update_note(title=title, content='Updated content', tags=[])
    assert success is True

    result = storage.get_note(title=title)
    expected = '# Test Note\nTags: \n\nUpdated content'
    assert result == expected


def test_update_note_not_found(storage):
    success = storage.update_note(title='Non-existent', content='Content', tags=[])
    assert success is False

    success = storage.update_note(
        filename='non_existent.md', content='Content', tags=[]
    )
    assert success is False


def test_update_note_no_identifier(storage):
    success = storage.update_note(content='Content', tags=[])
    assert success is False
