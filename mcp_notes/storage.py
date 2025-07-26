import json
import re
from pathlib import Path
from typing import List, Dict, Optional


class Storage:
    def __init__(self, directory: Path | str):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.index_file = self.directory / 'notes_index.json'

    def _load_index(self) -> Dict[str, Dict[str, any]]:
        """Load the notes index from JSON file."""
        if not self.index_file.exists():
            return {}

        with open(self.index_file, 'r') as f:
            return json.load(f)

    def _save_index(self, index: Dict[str, Dict[str, any]]) -> None:
        """Save the notes index to JSON file."""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)

    def _title_to_filename(self, title: str) -> str:
        """Convert title to filename, replacing non-alphanumeric chars with underscores."""
        # Replace all non-alphanumeric characters with underscores
        filename = re.sub(r'[^a-zA-Z0-9]', '_', title.lower())
        # Remove consecutive underscores and trailing underscores
        filename = re.sub(r'_+', '_', filename).strip('_')
        return f'{filename}.md'

    def _ensure_unique_filename(self, base_filename: str) -> str:
        """Ensure filename is unique by appending numbers if needed."""
        filename = base_filename
        counter = 1

        while (self.directory / filename).exists():
            name_part = base_filename.rsplit('.', 1)[0]
            filename = f'{name_part}_{counter}.md'
            counter += 1

        return filename

    def add_note(self, title: str, content: str, tags: List[str]) -> Path:
        """Create a new note file with given title, content and tags."""
        # Generate filename
        base_filename = self._title_to_filename(title)
        filename = self._ensure_unique_filename(base_filename)
        note_path = self.directory / filename

        # Format note content
        tags_str = ', '.join(tags) if tags else ''
        note_content = f'# {title}\nTags: {tags_str}\n\n{content}'

        # Write note file
        with open(note_path, 'w') as f:
            f.write(note_content)

        # Update index
        index = self._load_index()
        index[title] = {'filename': filename, 'tags': tags}
        self._save_index(index)

        return note_path

    def get_note(self, *, filename: str) -> Optional[str]:
        """Retrieve a note by filename."""
        note_path = self.directory / filename
        if not note_path.exists():
            return None

        with open(note_path, 'r') as f:
            return f.read()

    def list_notes(self) -> List[Dict[str, any]]:
        """List all notes in the directory."""
        index = self._load_index()
        return [
            {'filename': data['filename'], 'title': title, 'tags': data['tags']}
            for title, data in index.items()
        ]

    def delete_note(self, *, filename: str) -> bool:
        """Delete a note by filename."""
        note_path = self.directory / filename
        if not note_path.exists():
            return False

        # Find title by filename and remove from index
        index = self._load_index()
        title_to_delete = None
        for title, data in index.items():
            if data['filename'] == filename:
                title_to_delete = title
                break

        if title_to_delete:
            del index[title_to_delete]
            self._save_index(index)

        # Delete file
        note_path.unlink()
        return True

    def update_note(self, *, filename: str, content: str, tags: List[str]) -> bool:
        """Update an existing note's content and tags by filename."""
        note_path = self.directory / filename
        if not note_path.exists():
            return False

        # Find title by filename
        index = self._load_index()
        title = None
        for t, data in index.items():
            if data['filename'] == filename:
                title = t
                break

        if not title:
            return False

        # Format updated note content (preserve original title)
        tags_str = ', '.join(tags) if tags else ''
        note_content = f'# {title}\nTags: {tags_str}\n\n{content}'

        # Write updated note file
        with open(note_path, 'w') as f:
            f.write(note_content)

        # Update index with new tags
        index[title]['tags'] = tags
        self._save_index(index)

        return True
