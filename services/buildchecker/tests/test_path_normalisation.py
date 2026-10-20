"""Self-authored extension test (241880335).

Existing boundary tests cover failed opens, outside-project paths that never
share the project prefix, and ``chdir`` inheritance at fork.  They do not cover
the case where a *relative* path walks out of the project and back in, or out
to a sibling directory whose name merely starts with the project prefix.

``project_path`` normalises with ``posixpath.normpath`` before comparing, so
``headers/../needed.h`` and ``../project/needed2.h`` must both resolve to real
files inside the project, while ``../project-other/secret.h`` must not, even
though the string ``/course/project-other/...`` starts with ``/course/project``.
The same applies to duplicate spellings of one real file: they must collapse to
a single dependency instead of inflating the actual graph.
"""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import execution_graph


class TestPathNormalisation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.root = "/course/project"

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, text):
        path = self.folder / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_parent_relative_paths_are_normalised_before_the_project_filter(self):
        self.write("t.10", 'execve("/usr/bin/make", ["make", "app"], []) = 0\n'
                           'clone(child_stack=NULL, flags=SIGCHLD) = 11\n')
        self.write("t.11", 'execve("/usr/bin/cc", ["cc", "-c", "unit.c", "-o", "unit.o"], []) = 0\n'
                           'clone(child_stack=NULL, flags=SIGCHLD) = 12\n'
                           'clone(child_stack=NULL, flags=SIGCHLD) = 13\n')
        self.write("t.12", 'execve("/usr/bin/cc1", ["cc1", "unit.c"], []) = 0\n'
                           'openat(AT_FDCWD, "unit.c", O_RDONLY) = 3\n'
                           'openat(AT_FDCWD, "needed.h", O_RDONLY) = 4\n'
                           # Duplicate spelling of needed.h: must not add a second entry.
                           'openat(AT_FDCWD, "headers/../needed.h", O_RDONLY) = 5\n'
                           # Leaves the project and re-enters it: a real dependency.
                           'openat(AT_FDCWD, "../project/needed2.h", O_RDONLY) = 6\n'
                           # Leaves the project entirely: not a dependency.
                           'openat(AT_FDCWD, "../../etc/passwd", O_RDONLY) = 7\n'
                           # Sibling directory sharing the prefix: not a dependency.
                           'openat(AT_FDCWD, "../project-other/secret.h", O_RDONLY) = 8\n')
        self.write("t.13", 'execve("/usr/bin/as", ["as", "-o", "unit.o"], []) = 0\n'
                           'openat(AT_FDCWD, "unit.o", O_RDWR|O_CREAT|O_TRUNC, 0666) = 3\n')

        targets, _ = execution_graph(self.folder, self.root)
        dependencies = targets["unit.o"]["dependencies"]

        self.assertEqual(set(dependencies), {"unit.c", "needed.h", "needed2.h"})
        self.assertNotIn("../project-other/secret.h", dependencies)
        self.assertNotIn("passwd", dependencies)
        self.assertEqual(
            len(dependencies), len(set(dependencies)),
            "Normalised duplicate spellings must collapse into one dependency entry",
        )


if __name__ == "__main__":
    unittest.main()
