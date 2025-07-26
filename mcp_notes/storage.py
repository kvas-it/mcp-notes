import json
import re
from pathlib import Path
from typing import List, Dict, Optional


class Storage:
    def __init__(self, directory: Path | str):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.index_file = self.directory / 'notes_index.json'

    def _get_index_path(self, subdirectory: Optional[Path] = None) -> Path:
        """Get the path to the index file for a given directory."""
        if subdirectory is None:
            return self.index_file
        return subdirectory / 'notes_index.json'

    def _get_directory_for_note(self, filename: str) -> Path:
        """Get the directory where a note should be stored based on its filename."""
        if '/' in filename:
            # Handle nested path like "parent_name/child_name.md"
            parent_parts = filename.split('/')[:-1]  # Remove the filename part
            return self.directory / Path(*parent_parts)
        return self.directory

    def _normalize_parent(self, parent: Optional[str]) -> Optional[str]:
        """Normalize parent parameter by removing .md extension if present."""
        if parent is None:
            return None
        # Remove .md extension if present
        if parent.endswith('.md'):
            parent = parent[:-3]
        return parent

    def _calculate_children_count(self, note_filename: str) -> int:
        """Calculate the number of immediate child notes for a given note."""
        # Remove .md extension to get directory name
        if note_filename.endswith('.md'):
            dir_name = note_filename[:-3]
        else:
            dir_name = note_filename

        # Handle nested paths - get the full directory path
        if '/' in dir_name:
            child_dir = self.directory / dir_name
        else:
            child_dir = self.directory / dir_name

        if not child_dir.exists():
            return 0

        # Load the child directory's index
        child_index = self._load_index(child_dir)
        return len(child_index)

    def _calculate_descendant_count(self, note_filename: str) -> int:
        """Calculate the total number of descendant notes recursively."""
        # Remove .md extension to get directory name
        if note_filename.endswith('.md'):
            dir_name = note_filename[:-3]
        else:
            dir_name = note_filename

        # Handle nested paths - get the full directory path
        if '/' in dir_name:
            child_dir = self.directory / dir_name
        else:
            child_dir = self.directory / dir_name

        if not child_dir.exists():
            return 0

        total_count = 0
        child_index = self._load_index(child_dir)

        # Count immediate children
        total_count += len(child_index)

        # Recursively count descendants of each child
        for title, data in child_index.items():
            child_filename = data['filename']
            # For nested children, we need to get just the filename part
            if '/' in child_filename:
                # Get the relative path from the child directory
                relative_filename = (
                    child_filename.split('/', 1)[1]
                    if '/' in child_filename
                    else child_filename
                )
                full_child_path = f'{dir_name}/{relative_filename}'
            else:
                full_child_path = f'{dir_name}/{child_filename}'
            total_count += self._calculate_descendant_count(full_child_path)

        return total_count

    def _update_parent_counts(self, filename: str, count_delta: int) -> None:
        """Update children-count and descendant-count for all parents in the hierarchy."""
        if '/' not in filename:
            # Top-level note, no parents to update
            return

        # Get parent path
        parent_parts = filename.split('/')[:-1]

        # Update counts for each level in the hierarchy
        current_path = ''
        for i, part in enumerate(parent_parts):
            if i == 0:
                current_path = part
                parent_dir = self.directory
            else:
                current_path = f'{current_path}/{part}'
                parent_dir = self.directory / '/'.join(parent_parts[:i])

            # Load parent index
            parent_index = self._load_index(
                parent_dir if parent_dir != self.directory else None
            )

            # Find the parent note entry
            parent_note_name = None
            for title, data in parent_index.items():
                expected_filename = (
                    f'{part}.md' if i == 0 else f'{"/".join(parent_parts[: i + 1])}.md'
                )
                if (
                    data['filename'] == expected_filename
                    or data['filename'] == f'{part}.md'
                ):
                    parent_note_name = title
                    break

            if parent_note_name:
                # Recalculate actual counts
                parent_filename = parent_index[parent_note_name]['filename']
                children_count = self._calculate_children_count(parent_filename)
                descendant_count = self._calculate_descendant_count(parent_filename)

                # Update counts in index (only if > 0)
                if children_count > 0:
                    parent_index[parent_note_name]['children-count'] = children_count
                    parent_index[parent_note_name]['descendant-count'] = (
                        descendant_count
                    )
                else:
                    # Remove count keys if no children
                    parent_index[parent_note_name].pop('children-count', None)
                    parent_index[parent_note_name].pop('descendant-count', None)

                # Save updated parent index
                self._save_index(
                    parent_index, parent_dir if parent_dir != self.directory else None
                )

    def _load_index(
        self, subdirectory: Optional[Path] = None
    ) -> Dict[str, Dict[str, any]]:
        """Load the notes index from JSON file."""
        index_path = self._get_index_path(subdirectory)
        if not index_path.exists():
            return {}

        with open(index_path, 'r') as f:
            return json.load(f)

    def _save_index(
        self, index: Dict[str, Dict[str, any]], subdirectory: Optional[Path] = None
    ) -> None:
        """Save the notes index to JSON file with updated counts."""
        # Update counts for each entry before saving
        for title, data in index.items():
            filename = data['filename']
            children_count = self._calculate_children_count(filename)
            descendant_count = self._calculate_descendant_count(filename)

            # Only add count keys if there are children
            if children_count > 0:
                data['children-count'] = children_count
                data['descendant-count'] = descendant_count
            else:
                # Remove count keys if no children
                data.pop('children-count', None)
                data.pop('descendant-count', None)

        index_path = self._get_index_path(subdirectory)
        # Ensure the directory exists
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, 'w') as f:
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

    def _ensure_unique_filename_in_dir(
        self, base_filename: str, directory: Path
    ) -> str:
        """Ensure filename is unique in a specific directory by appending numbers if needed."""
        filename = base_filename
        counter = 1

        while (directory / filename).exists():
            name_part = base_filename.rsplit('.', 1)[0]
            filename = f'{name_part}_{counter}.md'
            counter += 1

        return filename

    def add_note(
        self, title: str, content: str, tags: List[str], parent: Optional[str] = None
    ) -> Path:
        """Create a new note file with given title, content and tags."""
        parent = self._normalize_parent(parent)

        # Generate base filename
        base_filename = self._title_to_filename(title)

        # Determine target directory and full filename
        if parent:
            # Create subdirectory for parent note
            parent_dir = self.directory / parent
            parent_dir.mkdir(parents=True, exist_ok=True)

            # Check for unique filename in the parent directory
            filename = self._ensure_unique_filename_in_dir(base_filename, parent_dir)
            full_filename = f'{parent}/{filename}'
            note_path = parent_dir / filename
            target_dir = parent_dir
        else:
            # Top-level note
            filename = self._ensure_unique_filename(base_filename)
            full_filename = filename
            note_path = self.directory / filename
            target_dir = self.directory

        # Format note content
        tags_str = ', '.join(tags) if tags else ''
        note_content = f'# {title}\nTags: {tags_str}\n\n{content}'

        # Write note file
        with open(note_path, 'w') as f:
            f.write(note_content)

        # Update index in the appropriate directory
        index = self._load_index(target_dir if parent else None)
        index[title] = {'filename': full_filename, 'tags': tags}
        self._save_index(index, target_dir if parent else None)

        # Update parent counts if this is a child note
        if parent:
            self._update_parent_counts(full_filename, 1)

        return note_path

    def get_note(self, *, filename: str) -> Optional[str]:
        """Retrieve a note by filename."""
        note_path = self.directory / filename
        if not note_path.exists():
            return None

        with open(note_path, 'r') as f:
            return f.read()

    def list_notes(self, parent: Optional[str] = None) -> List[Dict[str, any]]:
        """List notes in the directory or a specific parent subdirectory."""
        parent = self._normalize_parent(parent)

        if parent:
            # List notes in specific subdirectory
            parent_dir = self.directory / parent
            if not parent_dir.exists():
                return []
            index = self._load_index(parent_dir)
        else:
            # List top-level notes
            index = self._load_index()

        result = []
        for title, data in index.items():
            note_info = {
                'filename': data['filename'],
                'title': title,
                'tags': data['tags'],
            }
            # Add count information if present
            if 'children-count' in data:
                note_info['children_count'] = data['children-count']
            if 'descendant-count' in data:
                note_info['descendant_count'] = data['descendant-count']
            result.append(note_info)
        return result

    def delete_note(self, *, filename: str) -> bool:
        """Delete a note by filename."""
        note_path = self.directory / filename
        if not note_path.exists():
            return False

        # Determine which directory's index to update
        note_dir = self._get_directory_for_note(filename)
        target_dir = note_dir if note_dir != self.directory else None

        # Find title by filename and remove from index
        index = self._load_index(target_dir)
        title_to_delete = None
        for title, data in index.items():
            if data['filename'] == filename:
                title_to_delete = title
                break

        if title_to_delete:
            del index[title_to_delete]
            self._save_index(index, target_dir)

        # Delete file
        note_path.unlink()

        # Update parent counts if this was a child note
        if target_dir and note_dir != self.directory:
            self._update_parent_counts(filename, -1)

        # Clean up empty directory if this was the last note in a subdirectory
        if target_dir and note_dir != self.directory:
            self._cleanup_empty_directory(note_dir)

        return True

    def _cleanup_empty_directory(self, directory: Path) -> None:
        """Remove directory if it only contains an empty index file or is completely empty."""
        if not directory.exists() or directory == self.directory:
            return

        # Check if directory only contains an empty index file
        index_file = directory / 'notes_index.json'
        directory_contents = list(directory.iterdir())

        if not directory_contents:
            # Directory is completely empty
            directory.rmdir()
        elif len(directory_contents) == 1 and directory_contents[0] == index_file:
            # Check if index file is empty
            index = self._load_index(directory)
            if not index:
                # Remove empty index file and directory
                index_file.unlink()
                directory.rmdir()

    def update_note(self, *, filename: str, content: str, tags: List[str]) -> bool:
        """Update an existing note's content and tags by filename."""
        note_path = self.directory / filename
        if not note_path.exists():
            return False

        # Determine which directory's index to update
        note_dir = self._get_directory_for_note(filename)
        target_dir = note_dir if note_dir != self.directory else None

        # Find title by filename
        index = self._load_index(target_dir)
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
        self._save_index(index, target_dir)

        return True
