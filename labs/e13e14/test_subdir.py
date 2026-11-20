import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from orchestrate import snapshot


class SnapshotTests(unittest.TestCase):
    def test_single_source_subdirectory_and_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / 'repo'
            project = repo / 'nested'
            project.mkdir(parents=True)
            (project / 'main.c').write_text('int main(void) { return 0; }\n')
            (project / 'config.h').write_text('#define VALUE 1\n')
            (project / '.lab-project.json').write_text(json.dumps({
                'targets': [{'object': 'main.o', 'source': 'main.c'}],
                'build_target': 'main', 'program': 'main'}))
            def git(*args):
                return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()
            git('init')
            git('add', '.')
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'fixture')
            sha = git('rev-parse', 'HEAD')
            actual, path = snapshot(repo, sha, root / 'copy', root / 'logs', 'nested')
            self.assertEqual(actual, sha)
            self.assertEqual(path, (root / 'copy/nested').resolve())
            with self.assertRaisesRegex(ValueError, 'escapes snapshot'):
                snapshot(repo, sha, root / 'escape', root / 'logs', '../../repo')


if __name__ == '__main__':
    unittest.main()
