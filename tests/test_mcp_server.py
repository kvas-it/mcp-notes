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
async def test_get_note_by_title_success(mcp_server):
    """Test retrieving a note by title."""
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

        # Now get it
        result = await client.call_tool('get_note', {'title': 'Retrievable Note'})

        assert '# Retrievable Note' in result.data
        assert 'Content to retrieve' in result.data


@pytest.mark.asyncio
async def test_get_note_by_filename_success(mcp_server):
    """Test retrieving a note by filename."""
    # First add a note
    async with Client(mcp_server) as client:
        await client.call_tool(
            'add_note', {'title': 'File Note', 'content': 'File content', 'tags': []}
        )

        # Now get it by filename
        result = await client.call_tool('get_note', {'filename': 'file_note.md'})

        assert '# File Note' in result.data


@pytest.mark.asyncio
async def test_get_note_not_found(mcp_server):
    """Test getting a non-existent note."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool('get_note', {'title': 'Non-existent'})
        assert 'not found' in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_note_no_parameters(mcp_server):
    """Test getting a note without providing title or filename."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool('get_note', {})
        assert 'Must provide either title or filename' in str(exc_info.value)


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
async def test_delete_note_by_title_success(mcp_server):
    """Test deleting a note by title."""
    async with Client(mcp_server) as client:
        # Add a note
        await client.call_tool(
            'add_note',
            {'title': 'Delete Me', 'content': 'Content to delete', 'tags': ['delete']},
        )

        # Delete it
        result = await client.call_tool('delete_note', {'title': 'Delete Me'})

        assert 'deleted' in result.data

        # Verify it's gone
        with pytest.raises(Exception) as exc_info:
            await client.call_tool('get_note', {'title': 'Delete Me'})
        assert 'not found' in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_note_by_filename_success(mcp_server):
    """Test deleting a note by filename."""
    async with Client(mcp_server) as client:
        # Add a note
        await client.call_tool(
            'add_note', {'title': 'Delete by File', 'content': 'Content', 'tags': []}
        )

        # Delete by filename
        result = await client.call_tool(
            'delete_note', {'filename': 'delete_by_file.md'}
        )

        assert 'deleted' in result.data


@pytest.mark.asyncio
async def test_delete_note_not_found(mcp_server):
    """Test deleting a non-existent note."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool('delete_note', {'title': 'Non-existent'})
        assert 'not found' in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_note_no_parameters(mcp_server):
    """Test deleting without providing title or filename."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool('delete_note', {})
        assert 'Must provide either title or filename' in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_note_by_title_success(mcp_server):
    """Test updating a note by title."""
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
                'title': 'Update Test',
                'content': 'Updated content',
                'tags': ['updated', 'test'],
            },
        )

        assert 'updated' in result.data
        assert 'Update Test' in result.data

        # Verify the update
        get_result = await client.call_tool('get_note', {'title': 'Update Test'})
        assert 'Updated content' in get_result.data
        assert 'updated, test' in get_result.data


@pytest.mark.asyncio
async def test_update_note_by_filename_success(mcp_server):
    """Test updating a note by filename."""
    async with Client(mcp_server) as client:
        # Add a note
        await client.call_tool(
            'add_note',
            {'title': 'File Update', 'content': 'Original', 'tags': ['file']},
        )

        # Update by filename
        result = await client.call_tool(
            'update_note',
            {
                'filename': 'file_update.md',
                'content': 'Updated via filename',
                'tags': ['updated'],
            },
        )

        assert 'updated' in result.data

        # Verify the update
        get_result = await client.call_tool('get_note', {'filename': 'file_update.md'})
        assert 'Updated via filename' in get_result.data


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
            {'title': 'No Tags Update', 'content': 'Updated without tags'},
        )

        assert 'updated' in result.data

        # Verify the update (should have empty tags)
        get_result = await client.call_tool('get_note', {'title': 'No Tags Update'})
        assert 'Updated without tags' in get_result.data
        assert 'Tags: \n\n' in get_result.data


@pytest.mark.asyncio
async def test_update_note_not_found(mcp_server):
    """Test updating a non-existent note."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool(
                'update_note',
                {'title': 'Non-existent', 'content': 'Content', 'tags': []},
            )
        assert 'not found' in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_note_no_parameters(mcp_server):
    """Test updating without providing title or filename."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool('update_note', {'content': 'Content', 'tags': []})
        assert 'Must provide either title or filename' in str(exc_info.value)
