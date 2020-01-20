# SPDX-FileCopyrightText: 2017-2019 Free Software Foundation Europe e.V.
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for reuse.project."""

# pylint: disable=invalid-name,protected-access

import os
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import pytest
from license_expression import LicenseSymbol

from reuse import _util
from reuse.project import Project

git = pytest.mark.skipif(not _util.GIT_EXE, reason="requires git")
posix = pytest.mark.skipif(
    sys.platform == "win32", reason="Windows not supported"
)

TESTS_DIRECTORY = Path(__file__).parent.resolve()
RESOURCES_DIRECTORY = TESTS_DIRECTORY / "resources"


def test_project_not_a_directory(empty_directory):
    """Cannot create a Project without a valid directory."""
    (empty_directory / "foo.py").touch()
    with pytest.raises(NotADirectoryError):
        Project(empty_directory / "foo.py")


def test_all_files(empty_directory):
    """Given a directory with some files, yield all files."""
    (empty_directory / "foo").touch()
    (empty_directory / "bar").touch()

    project = Project(empty_directory)
    assert {file_.name for file_ in project.all_files()} == {"foo", "bar"}


def test_all_files_ignore_dot_license(empty_directory):
    """When file and file.license are present, only yield file."""
    (empty_directory / "foo").touch()
    (empty_directory / "foo.license").touch()

    project = Project(empty_directory)
    assert {file_.name for file_ in project.all_files()} == {"foo"}


def test_all_files_ignore_git(empty_directory):
    """When the git directory is present, ignore it."""
    (empty_directory / ".git").mkdir()
    (empty_directory / ".git/config").touch()

    project = Project(empty_directory)
    assert not list(project.all_files())


@git
def test_all_files_git_ignored(git_repository):
    """Given a Git repository where some files are ignored, do not yield those
    files.
    """
    project = Project(git_repository)
    assert Path("build/hello.py").absolute() not in project.all_files()


@git
def test_all_files_git_ignored_different_cwd(git_repository):
    """Given a Git repository where some files are ignored, do not yield those
    files.

    Be in a different CWD during the above.
    """
    os.chdir(git_repository / "LICENSES")
    project = Project(git_repository)
    assert Path("build/hello.py").absolute() not in project.all_files()


@git
def test_all_files_git_ignored_contains_space(git_repository):
    """Files that contain spaces are also ignored."""
    (git_repository / "I contain spaces.pyc").touch()
    project = Project(git_repository)
    assert Path("I contain spaces.pyc").absolute() not in project.all_files()


@git
@posix
def test_all_files_git_ignored_contains_newline(git_repository):
    """Files that contain newlines are also ignored."""
    (git_repository / "hello\nworld.pyc").touch()
    project = Project(git_repository)
    assert Path("hello\nworld.pyc").absolute() not in project.all_files()


def test_spdx_info_of_file_does_not_exist(fake_repository):
    """Raise FileNotFoundError when asking for the SPDX info of a file that
    does not exist.
    """
    project = Project(fake_repository)
    with pytest.raises(FileNotFoundError):
        project.spdx_info_of(fake_repository / "does_not_exist")


def test_spdx_info_of_directory(empty_directory):
    """Raise IsADirectoryError when calling spdx_info_of on a directory."""
    (empty_directory / "src").mkdir()

    project = Project(empty_directory)
    with pytest.raises((IsADirectoryError, PermissionError)):
        project.spdx_info_of(empty_directory / "src")


def test_spdx_info_of_unlicensed_file(fake_repository):
    """Return an empty SpdxInfo object when asking for the SPDX information
    of a file that has no SPDX information.
    """
    (fake_repository / "foo.py").touch()
    project = Project(fake_repository)
    assert not any(project.spdx_info_of("foo.py"))


def test_spdx_info_of_only_copyright(fake_repository):
    """A file contains only a copyright line. Test whether it correctly picks
    up on that.
    """
    (fake_repository / "foo.py").write_text(
        "SPDX-FileCopyrightText: 2017 Mary Sue"
    )
    project = Project(fake_repository)
    spdx_info = project.spdx_info_of("foo.py")
    assert not any(spdx_info.spdx_expressions)
    assert len(spdx_info.copyright_lines) == 1
    assert (
        spdx_info.copyright_lines.pop()
        == "SPDX-FileCopyrightText: 2017 Mary Sue"
    )


def test_spdx_info_of_only_copyright_also_covered_by_debian(fake_repository):
    """A file contains only a copyright line, but debian/copyright also has
    information on this file. Use both.
    """
    (fake_repository / "doc/foo.py").write_text(
        "SPDX-FileCopyrightText: in file"
    )
    project = Project(fake_repository)
    spdx_info = project.spdx_info_of("doc/foo.py")
    assert any(spdx_info.spdx_expressions)
    assert len(spdx_info.copyright_lines) == 2
    assert "SPDX-FileCopyrightText: in file" in spdx_info.copyright_lines
    assert "2017 Mary Sue" in spdx_info.copyright_lines


def test_spdx_info_of_also_covered_by_dep5(fake_repository):
    """A file contains all SPDX information, but .reuse/dep5 also
    provides information on this file. Use both.
    """
    (fake_repository / "doc/foo.py").write_text(
        dedent(
            """
            SPDX-License-Identifier: MIT
            SPDX-FileCopyrightText: in file"""
        )
    )
    project = Project(fake_repository)
    spdx_info = project.spdx_info_of("doc/foo.py")
    assert LicenseSymbol("MIT") in spdx_info.spdx_expressions
    assert LicenseSymbol("CC0-1.0") in spdx_info.spdx_expressions
    assert "SPDX-FileCopyrightText: in file" in spdx_info.copyright_lines
    assert "2017 Mary Sue" in spdx_info.copyright_lines


def test_spdx_info_of_no_duplicates(empty_directory):
    """A file contains the same lines twice. The SpdxInfo only contains those
    lines once.
    """
    spdx_line = "SPDX-License-Identifier: GPL-3.0-or-later\n"
    copyright_line = (
        "SPDX-FileCopyrightText: 2017 Free Software Foundation Europe\n"
    )
    text = spdx_line + copyright_line

    (empty_directory / "foo.py").write_text(text * 2)
    project = Project(empty_directory)
    spdx_info = project.spdx_info_of("foo.py")
    assert len(spdx_info.spdx_expressions) == 1
    assert LicenseSymbol("GPL-3.0-or-later") in spdx_info.spdx_expressions
    assert len(spdx_info.copyright_lines) == 1
    assert (
        "SPDX-FileCopyrightText: 2017 Free Software Foundation Europe"
        in spdx_info.copyright_lines
    )


def test_spdx_info_of_binary_succeeds(fake_repository):
    """spdx_info_of succeeds when the target is covered by dep5."""
    shutil.copy(
        RESOURCES_DIRECTORY / "fsfe.png", fake_repository / "doc/fsfe.png"
    )

    project = Project(fake_repository)
    spdx_info = project.spdx_info_of("doc/fsfe.png")
    assert LicenseSymbol("CC0-1.0") in spdx_info.spdx_expressions


def test_license_file_detected(empty_directory):
    """Test whether---when given a file and a license file---the license file
    is detected and read.
    """
    (empty_directory / "foo.py").touch()
    (empty_directory / "foo.py.license").write_text(
        "SPDX-FileCopyrightText: 2017 Mary Sue\nSPDX-License-Identifier: MIT\n"
    )

    project = Project(empty_directory)
    spdx_info = project.spdx_info_of("foo.py")

    assert "SPDX-FileCopyrightText: 2017 Mary Sue" in spdx_info.copyright_lines
    assert LicenseSymbol("MIT") in spdx_info.spdx_expressions


def test_licenses_filename(empty_directory):
    """Detect the license identifier of a license from its stem."""
    (empty_directory / "LICENSES").mkdir()
    (empty_directory / "LICENSES/foo.txt").touch()
    project = Project(empty_directory)
    assert "foo" in project.licenses


def test_licenses_no_extension(empty_directory):
    """Detect the license identifier of a license from its full name if it is
    in the license list.
    """
    (empty_directory / "LICENSES").mkdir()
    (empty_directory / "LICENSES/GPL-3.0-or-later").touch()
    (empty_directory / "LICENSES/MIT-3.0-or-later").touch()
    project = Project(empty_directory)
    assert "GPL-3.0-or-later" in project.licenses
    assert "MIT-3" in project.licenses


def test_licenses_subdirectory(empty_directory):
    """Find a license in a subdirectory of LICENSES/."""
    (empty_directory / "LICENSES/sub").mkdir(parents=True)
    (empty_directory / "LICENSES/sub/MIT.txt").touch()
    project = Project(empty_directory)
    assert "MIT" in project.licenses


def test_relative_from_root(empty_directory):
    """A simple test. Given /path/to/root/src/hello.py, return src/hello.py."""
    project = Project(empty_directory)
    assert project._relative_from_root(project.root / "src/hello.py") == Path(
        "src/hello.py"
    )


def test_relative_from_root_no_shared_base_path(empty_directory):
    """A path can still be relative from root if the paths do not have a common
    prefix.

    For instance, if root is /path/to/root and given root/src/hello.py from the
    directory /path/to, return src/hello.py. This is a bit involved, but works
    out.
    """
    project = Project(empty_directory)
    parent = empty_directory.parent
    os.chdir(parent)
    assert project._relative_from_root(
        Path(f"{project.root.name}/src/hello.py")
    ) == Path("src/hello.py")
