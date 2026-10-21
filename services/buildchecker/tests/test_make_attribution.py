"""Self-authored extension test (221900015).

``job_for`` maps every pid to its *direct child of the single Make process*, so
the Make process itself ends up with ``job_pid=None``.  ``execution_graph``
depends on that distinction in two opposite directions:

* Make reading its own database inputs (``Makefile``, included makefiles) must
  never be recorded as a compiler input, otherwise every target would gain a
  bogus dependency on the Makefile;
* Make writing a project file outside a recipe process must be rejected loudly,
  because such a write has no job to attribute it to and would otherwise be
  dropped from the actual graph without any trace of the loss.

The existing boundary tests cover sibling-process joins, failed opens,
fork-time ``chdir`` inheritance, deleted outputs, multi-output jobs and
numeric-FD paths, but none of them exercises the ``job is None`` branch that
this file pins down.
"""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import Unsupported, execution_graph


class TestMakeAttribution(unittest.TestCase):
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

    def write_recipe(self):
        self.write("t.11", 'execve("/usr/bin/cc", ["cc", "-c", "unit.c", "-o", "unit.o"], []) = 0\n'
                           'openat(AT_FDCWD, "unit.c", O_RDONLY) = 3\n'
                           'openat(AT_FDCWD, "unit.o", O_RDWR|O_CREAT|O_TRUNC, 0666) = 4\n')

    def test_make_reading_its_own_inputs_is_not_a_compiler_dependency(self):
        self.write("t.10", 'execve("/usr/bin/make", ["make", "app"], []) = 0\n'
                           'openat(AT_FDCWD, "Makefile", O_RDONLY) = 3\n'
                           'openat(AT_FDCWD, "config.h", O_RDONLY) = 4\n'
                           'clone(child_stack=NULL, flags=SIGCHLD) = 11\n')
        self.write_recipe()

        targets, processes = execution_graph(self.folder, self.root)

        self.assertEqual(set(targets), {"unit.o"})
        self.assertEqual(set(targets["unit.o"]["dependencies"]), {"unit.c"})
        self.assertNotIn("Makefile", targets["unit.o"]["dependencies"])
        self.assertNotIn("config.h", targets["unit.o"]["dependencies"])
        make = next(p for p in processes if p["pid"] == 10)
        self.assertIsNone(make["job_pid"], "The Make process itself never owns a recipe job")
        self.assertEqual(targets["unit.o"]["job_pid"], 11)

    def test_make_writing_a_project_file_outside_a_recipe_is_rejected(self):
        self.write("t.10", 'execve("/usr/bin/make", ["make", "app"], []) = 0\n'
                           'openat(AT_FDCWD, "app", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 3\n'
                           'clone(child_stack=NULL, flags=SIGCHLD) = 11\n')
        self.write_recipe()

        with self.assertRaises(Unsupported) as caught:
            execution_graph(self.folder, self.root)

        self.assertIn("outside a recipe process", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
