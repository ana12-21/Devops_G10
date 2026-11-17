"""Personal E11-E12 contracts: patch placement per Makefile style and stale-report guards."""
import tempfile
import unittest
from pathlib import Path

import pipeline
from lab import commit, fixture, patch, scan


class StudentContract221900015(unittest.TestCase):
    def project(self, root, style):
        project = root/('project-'+style)
        fixture(project, style)
        (project/'main.c').write_text('#include "extra.h"\n'+(project/'main.c').read_text(), encoding='utf-8')
        commit(project, 'add project include')
        return project

    def test_macro_style_patch_extends_the_variable(self):
        with tempfile.TemporaryDirectory() as d:
            project = self.project(Path(d), 'macro')
            report = scan(project)
            diff, edits = patch(project, report)
            self.assertEqual([(e['target'], e['dependency'], e['style']) for e in edits],
                             [('main.o', 'config.h', 'macro'), ('main.o', 'extra.h', 'macro')])
            self.assertIn('-DEPS = main.c unused.h\n', diff)
            self.assertIn('+DEPS = main.c unused.h config.h extra.h\n', diff)
            self.assertNotIn('main.o: ', diff)

    def test_mixed_style_patch_keeps_the_header_variable(self):
        with tempfile.TemporaryDirectory() as d:
            project = self.project(Path(d), 'mixed')
            report = scan(project)
            diff, edits = patch(project, report)
            self.assertEqual([e['style'] for e in edits], ['mixed', 'mixed'])
            self.assertIn('+main.o: main.c $(HEADERS) config.h extra.h\n', diff)

    def test_direct_style_patch_stays_on_the_rule_line(self):
        with tempfile.TemporaryDirectory() as d:
            project = self.project(Path(d), 'direct')
            report = scan(project)
            diff, edits = patch(project, report)
            self.assertEqual([e['style'] for e in edits], ['direct', 'direct'])
            self.assertIn('+main.o: main.c unused.h config.h extra.h\n', diff)

    def test_patch_refuses_stale_report_even_without_the_envelope_check(self):
        with tempfile.TemporaryDirectory() as d:
            project = self.project(Path(d), 'direct')
            report = scan(project)
            before = (project/'Makefile').read_text()
            report['commit'] = '0'*40
            with self.assertRaisesRegex(ValueError, 'STALE_REPORT'):
                patch(project, report)
            self.assertEqual((project/'Makefile').read_text(), before)

    def test_unsafe_dependency_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as d:
            project = self.project(Path(d), 'direct')
            report = scan(project)
            before = (project/'Makefile').read_text()
            for dep in ('../escape.h', '/etc/passwd', 'with space.h'):
                damaged = dict(report, findings=[{'type':'MISSING','target':'main.o','dependency':dep}])
                with self.assertRaises(ValueError):
                    patch(project, damaged)
                self.assertEqual((project/'Makefile').read_text(), before)

    def test_snapshot_refuses_projects_outside_the_profile(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project = root/'project'
            fixture(project, 'direct')
            (project/'helper.c').unlink()
            (project/'config.h').unlink()
            commit(project, 'drop helper and config')
            with self.assertRaises(pipeline.Failure) as caught:
                pipeline.snapshot(project, 'HEAD', root/'copy', root/'logs')
            self.assertEqual(caught.exception.code, 'UNSUPPORTED_PROJECT')


if __name__ == '__main__':
    unittest.main()
