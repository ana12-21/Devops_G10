"""Student test: Make's own reads are not compiler dependencies."""
import tempfile
from pathlib import Path

from buildchecker.fullcheck import execution_graph


def test_make_read_is_not_a_recipe_dependency():
    with tempfile.TemporaryDirectory() as directory:
        trace_dir = Path(directory)

        (trace_dir / "t.10").write_text(
            'execve("/usr/bin/make", ["make", "main.o"], []) = 0\n'
            'openat(AT_FDCWD, "make-only.h", O_RDONLY) = 3\n'
            'clone(child_stack=NULL, flags=SIGCHLD) = 11\n',
            encoding="utf-8",
        )

        (trace_dir / "t.11").write_text(
            'execve("/usr/bin/cc", '
            '["cc", "-c", "main.c", "-o", "main.o"], []) = 0\n'
            'openat(AT_FDCWD, "main.c", O_RDONLY) = 3\n'
            'openat(AT_FDCWD, "main.o", '
            'O_WRONLY|O_CREAT|O_TRUNC, 0666) = 4\n',
            encoding="utf-8",
        )

        targets, _ = execution_graph(trace_dir, "/course/project")

        assert set(targets) == {"main.o"}
        assert set(targets["main.o"]["dependencies"]) == {"main.c"}
        assert targets["main.o"]["processes"] == [11]
