import tempfile
from pathlib import Path

import pytest
from fastmcp import Client

from mcp_notes.mcp_server import app
from mcp_notes.storage import Storage


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def mcp_server(temp_dir):
    """Create FastMCP server with temporary storage for testing."""
    app.storage = Storage(temp_dir)
    return app


@pytest.mark.asyncio
async def test_add_note_success(mcp_server):
    """Test adding a note successfully."""
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            'add_note',
            {
                'title': 'Test Note',
                'content': 'This is test content',
                'tags': ['test', 'example'],
            },
        )

        assert 'Test Note' in result.data
        assert 'test_note.md' in result.data


@pytest.mark.asyncio
async def test_add_note_without_tags(mcp_server):
    """Test adding a note without tags."""
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            'add_note', {'title': 'No Tags Note', 'content': 'Content without tags'}
        )

        assert 'No Tags Note' in result.data


@pytest.mark.asyncio
async def test_get_note_by_filename_success(mcp_server):
    """Test retrieving a note by filename."""
    # First add a note
    async with Client(mcp_server) as client:
        await client.call_tool(
            'add_note',
            {
                'title': 'Retrievable Note',
                'content': 'Content to retrieve',
                'tags': ['retrieve'],
            },
        )

        # Now get it by filename
        result = await client.call_tool('get_note', {'filename': 'retrievable_note.md'})

        assert '# Retrievable Note' in result.data
        assert 'Content to retrieve' in result.data


@pytest.mark.asyncio
async def test_get_note_not_found(mcp_server):
    """Test getting a non-existent note."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool('get_note', {'filename': 'non_existent.md'})
        assert 'not found' in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_notes_empty(mcp_server):
    """Test listing notes when no notes exist."""
    async with Client(mcp_server) as client:
        result = await client.call_tool('list_notes', {})

        assert result.data == []


@pytest.mark.asyncio
async def test_list_notes_with_content(mcp_server):
    """Test listing notes when notes exist."""
    async with Client(mcp_server) as client:
        # Add a couple of notes
        await client.call_tool(
            'add_note',
            {'title': 'First Note', 'content': 'First content', 'tags': ['first']},
        )
        await client.call_tool(
            'add_note',
            {
                'title': 'Second Note',
                'content': 'Second content',
                'tags': ['second', 'test'],
            },
        )

        # List them
        result = await client.call_tool('list_notes', {})

        assert len(result.data) == 2
        titles = [note['title'] for note in result.data]
        assert 'First Note' in titles
        assert 'Second Note' in titles


@pytest.mark.asyncio
async def test_delete_note_by_filename_success(mcp_server):
    """Test deleting a note by filename."""
    async with Client(mcp_server) as client:
        # Add a note
        await client.call_tool(
            'add_note',
            {'title': 'Delete Me', 'content': 'Content to delete', 'tags': ['delete']},
        )

        # Delete it
        result = await client.call_tool('delete_note', {'filename': 'delete_me.md'})

        assert 'deleted' in result.data

        # Verify it's gone
        with pytest.raises(Exception) as exc_info:
            await client.call_tool('get_note', {'filename': 'delete_me.md'})
        assert 'not found' in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_note_not_found(mcp_server):
    """Test deleting a non-existent note."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool('delete_note', {'filename': 'non_existent.md'})
        assert 'not found' in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_note_by_filename_success(mcp_server):
    """Test updating a note by filename."""
    async with Client(mcp_server) as client:
        # Add a note
        await client.call_tool(
            'add_note',
            {
                'title': 'Update Test',
                'content': 'Original content',
                'tags': ['original'],
            },
        )

        # Update it
        result = await client.call_tool(
            'update_note',
            {
                'filename': 'update_test.md',
                'content': 'Updated content',
                'tags': ['updated', 'test'],
            },
        )

        assert 'updated' in result.data
        assert 'update_test.md' in result.data

        # Verify the update
        get_result = await client.call_tool('get_note', {'filename': 'update_test.md'})
        assert 'Updated content' in get_result.data
        assert 'updated, test' in get_result.data


@pytest.mark.asyncio
async def test_update_note_without_tags(mcp_server):
    """Test updating a note without providing tags."""
    async with Client(mcp_server) as client:
        # Add a note
        await client.call_tool(
            'add_note',
            {'title': 'No Tags Update', 'content': 'Original', 'tags': ['original']},
        )

        # Update without tags parameter
        result = await client.call_tool(
            'update_note',
            {'filename': 'no_tags_update.md', 'content': 'Updated without tags'},
        )

        assert 'updated' in result.data

        # Verify the update (should have empty tags)
        get_result = await client.call_tool(
            'get_note', {'filename': 'no_tags_update.md'}
        )
        assert 'Updated without tags' in get_result.data
        assert 'Tags: \n\n' in get_result.data


@pytest.mark.asyncio
async def test_update_note_not_found(mcp_server):
    """Test updating a non-existent note."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool(
                'update_note',
                {'filename': 'non_existent.md', 'content': 'Content', 'tags': []},
            )
        assert 'not found' in str(exc_info.value)


# Tests for hierarchical notes via MCP server
@pytest.mark.asyncio
async def test_add_note_with_parent(mcp_server):
    """Test adding a note with a parent via MCP server."""
    async with Client(mcp_server) as client:
        # Add parent note
        await client.call_tool(
            'add_note',
            {'title': 'Parent Note', 'content': 'Parent content', 'tags': ['parent']},
        )

        # Add child note
        result = await client.call_tool(
            'add_note',
            {
                'title': 'Child Note',
                'content': 'Child content',
                'tags': ['child'],
                'parent': 'parent_note',
            },
        )

        assert 'Child Note' in result.data
        assert 'child_note.md' in result.data


@pytest.mark.asyncio
async def test_hierarchical_get_note(mcp_server):
    """Test getting hierarchical notes via MCP server."""
    async with Client(mcp_server) as client:
        # Add parent and child notes
        await client.call_tool(
            'add_note',
            {'title': 'Parent Note', 'content': 'Parent content', 'tags': ['parent']},
        )
        await client.call_tool(
            'add_note',
            {
                'title': 'Child Note',
                'content': 'Child content',
                'tags': ['child'],
                'parent': 'parent_note',
            },
        )

        # Get child note using full path
        result = await client.call_tool(
            'get_note', {'filename': 'parent_note/child_note.md'}
        )

        assert '# Child Note' in result.data
        assert 'Child content' in result.data


@pytest.mark.asyncio
async def test_list_notes_hierarchical(mcp_server):
    """Test listing notes with hierarchy via MCP server."""
    async with Client(mcp_server) as client:
        # Add parent and child notes
        await client.call_tool(
            'add_note',
            {'title': 'Parent Note', 'content': 'Parent content', 'tags': ['parent']},
        )
        await client.call_tool(
            'add_note',
            {
                'title': 'Child Note 1',
                'content': 'Child content 1',
                'tags': ['child1'],
                'parent': 'parent_note',
            },
        )
        await client.call_tool(
            'add_note',
            {
                'title': 'Child Note 2',
                'content': 'Child content 2',
                'tags': ['child2'],
                'parent': 'parent_note',
            },
        )

        # List top-level notes (should only show parent)
        top_result = await client.call_tool('list_notes', {})
        assert len(top_result.data) == 1
        assert top_result.data[0]['title'] == 'Parent Note'

        # List notes in parent directory (should show children)
        child_result = await client.call_tool('list_notes', {'parent': 'parent_note'})
        assert len(child_result.data) == 2
        child_titles = {note['title'] for note in child_result.data}
        assert child_titles == {'Child Note 1', 'Child Note 2'}


@pytest.mark.asyncio
async def test_hierarchical_delete_note(mcp_server):
    """Test deleting hierarchical notes via MCP server."""
    async with Client(mcp_server) as client:
        # Add parent and child notes
        await client.call_tool(
            'add_note',
            {'title': 'Parent Note', 'content': 'Parent content', 'tags': ['parent']},
        )
        await client.call_tool(
            'add_note',
            {
                'title': 'Child Note',
                'content': 'Child content',
                'tags': ['child'],
                'parent': 'parent_note',
            },
        )

        # Delete child note
        result = await client.call_tool(
            'delete_note', {'filename': 'parent_note/child_note.md'}
        )
        assert 'deleted' in result.data

        # Verify child note is gone
        with pytest.raises(Exception) as exc_info:
            await client.call_tool(
                'get_note', {'filename': 'parent_note/child_note.md'}
            )
        assert 'not found' in str(exc_info.value)


@pytest.mark.asyncio
async def test_hierarchical_update_note(mcp_server):
    """Test updating hierarchical notes via MCP server."""
    async with Client(mcp_server) as client:
        # Add parent and child notes
        await client.call_tool(
            'add_note',
            {'title': 'Parent Note', 'content': 'Parent content', 'tags': ['parent']},
        )
        await client.call_tool(
            'add_note',
            {
                'title': 'Child Note',
                'content': 'Original child content',
                'tags': ['child'],
                'parent': 'parent_note',
            },
        )

        # Update child note
        result = await client.call_tool(
            'update_note',
            {
                'filename': 'parent_note/child_note.md',
                'content': 'Updated child content',
                'tags': ['updated', 'child'],
            },
        )
        assert 'updated' in result.data

        # Verify the update
        get_result = await client.call_tool(
            'get_note', {'filename': 'parent_note/child_note.md'}
        )
        assert 'Updated child content' in get_result.data
        assert 'updated, child' in get_result.data


@pytest.mark.asyncio
async def test_count_information_via_mcp(mcp_server):
    """Test that count information is exposed through MCP server."""
    async with Client(mcp_server) as client:
        # Add parent note
        await client.call_tool(
            'add_note',
            {
                'title': 'Parent Project',
                'content': 'Parent content',
                'tags': ['project'],
            },
        )

        # Initially no count information (no children)
        result = await client.call_tool('list_notes', {})
        parent_note = next(
            note for note in result.data if note['title'] == 'Parent Project'
        )
        assert parent_note['children_count'] is None
        assert parent_note['descendant_count'] is None

        # Add child notes
        await client.call_tool(
            'add_note',
            {
                'title': 'Task 1',
                'content': 'First task',
                'tags': ['task'],
                'parent': 'parent_project',
            },
        )
        await client.call_tool(
            'add_note',
            {
                'title': 'Task 2',
                'content': 'Second task',
                'tags': ['task'],
                'parent': 'parent_project',
            },
        )

        # Now should have count information
        result = await client.call_tool('list_notes', {})
        parent_note = next(
            note for note in result.data if note['title'] == 'Parent Project'
        )
        assert parent_note['children_count'] == 2
        assert parent_note['descendant_count'] == 2

        # Child notes should not have count information
        child_result = await client.call_tool(
            'list_notes', {'parent': 'parent_project'}
        )
        for child_note in child_result.data:
            assert child_note['children_count'] is None
            assert child_note['descendant_count'] is None
