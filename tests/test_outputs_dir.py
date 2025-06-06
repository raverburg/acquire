from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from dissect.target.helpers.fsutil import normalize

from acquire.outputs import DirectoryOutput

if TYPE_CHECKING:
    from pathlib import Path

    from dissect.target.filesystem import VirtualFilesystem


@pytest.fixture
def dir_output(tmp_path: Path) -> DirectoryOutput:
    tmp_path.mkdir(parents=True, exist_ok=True)
    return DirectoryOutput(tmp_path)


def leaves(path: Path) -> list[Path]:
    leave_paths = []

    dir_is_empty = True
    for entry in path.iterdir():
        dir_is_empty = False
        if entry.is_dir():
            leave_paths.extend(leaves(entry))
        else:
            leave_paths.append(entry)

    if dir_is_empty:
        leave_paths.append(path)

    return leave_paths


@pytest.mark.parametrize(
    "entry_name",
    [
        "/foo/bar/some-file",
        "/foo/bar/some-symlink",
        "/foo/bar/some-dir",
    ],
)
def test_dir_output_write_entry(mock_fs: VirtualFilesystem, dir_output: DirectoryOutput, entry_name: str) -> None:
    entry = mock_fs.get(entry_name)
    dir_output.write_entry(entry_name, entry)
    dir_output.close()

    path = dir_output.path
    files = leaves(path)

    assert len(files) == 1

    file = files[0]

    # Convert a os seperated file to the entry name.
    file_path = f"/{normalize(str(file.relative_to(path)), alt_separator=os.sep)}"
    assert file_path == entry_name

    if entry.is_dir():
        assert file.is_dir()
    elif entry.is_symlink() or entry.is_file():
        assert file.is_file()
