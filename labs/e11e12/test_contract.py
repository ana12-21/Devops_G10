import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pipeline
import server

class Contracts(unittest.TestCase):
    def report(self):return {'schema_version':'e11e12-1','kind':'incremental-check','commit':'a'*40,'status':'SUCCEEDED'}
    def test_accept_current_report(self):pipeline.check_envelope(self.report(),'a'*40,'incremental-check')
    def test_reject_old_commit(self):
        with self.assertRaisesRegex(pipeline.Failure,'another commit'):pipeline.check_envelope(self.report(),'b'*40)
    def test_reject_schema(self):
        r=self.report();r['schema_version']='old'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_failed_upstream(self):
        r=self.report();r['status']='FAILED'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_wrong_artifact_kind(self):
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(self.report(),'a'*40,'fixed-md')
    def test_artifact_uses_relative_uri_and_content_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'x.json';p.write_text('{}')
            a=pipeline.artifact(p,root,'job-1');self.assertEqual(a['uri'],'artifact://job-1/x.json');self.assertEqual(len(a['sha256']),64)
    def test_existing_evidence_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'keep').write_text('keep')
            with self.assertRaises(pipeline.Failure):pipeline.execute({},root)
            self.assertEqual((root/'keep').read_text(),'keep')
    def test_changed_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'r.json';p.write_text('{}')
            with self.assertRaises(pipeline.Failure):pipeline.load_artifact(p,'0'*64)
    def test_same_key_same_request_same_job(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);store=server.Store(root/'jobs')
            request={'mode':'e11-a','repo':str(pipeline.ROOT/'data/p'),'base':'a','target':'b'}
            with patch.object(store.pool,'submit'):
                one=store.submit(request,'same');two=store.submit(request,'same')
                self.assertEqual(one['job_id'],two['job_id'])
                changed=dict(request,target='c')
                with self.assertRaisesRegex(ValueError,'IDEMPOTENCY_CONFLICT'):store.submit(changed,'same')
            store.pool.shutdown()
    def test_api_rejects_repo_outside_data(self):
        with tempfile.TemporaryDirectory() as d:
            store=server.Store(Path(d)/'jobs')
            with self.assertRaises(ValueError):store.submit({'mode':'e11-a','repo':str(Path(d)),'base':'a','target':'b'},'k')
            store.pool.shutdown()

class StudentContracts(unittest.TestCase):
    """Student addition (241880335): E11-A compares an incremental report with a
    full BuildChecker report, but the two are not shaped alike.

    ``full_check`` observes the whole build, so ``findings.json`` also carries
    the link target ``app``.  ``scan`` only ever maps ``main.o``/``helper.o``.
    Comparing the raw lists would therefore always fail on ``app``, and
    comparing only the number of findings would accept a report that swapped
    one dependency for another.  ``pipeline.normalized`` is the single place
    that resolves this, so it deserves its own tests.
    """

    def test_link_target_is_dropped_from_the_comparison(self):
        full=[{'type':'MISSING','target':'app','dependency':'main.o'},
              {'type':'MISSING','target':'main.o','dependency':'config.h'}]
        self.assertEqual(pipeline.normalized(full), [('MISSING','main.o','config.h')])

    def test_comparison_is_order_insensitive_but_content_exact(self):
        left=[{'type':'REDUNDANT','target':'helper.o','dependency':'stale.h'},
              {'type':'MISSING','target':'main.o','dependency':'config.h'}]
        right=list(reversed(left))
        self.assertEqual(pipeline.normalized(left), pipeline.normalized(right))
        swapped=[{'type':'REDUNDANT','target':'helper.o','dependency':'stale.h'},
                 {'type':'MISSING','target':'main.o','dependency':'extra.h'}]
        self.assertNotEqual(pipeline.normalized(left), pipeline.normalized(swapped),
            'Same finding count but a different dependency must not compare equal')

    def test_full_and_incremental_agree_once_projected(self):
        full=[{'type':'MISSING','target':'app','dependency':'main.o'},
              {'type':'MISSING','target':'main.o','dependency':'config.h'},
              {'type':'REDUNDANT','target':'main.o','dependency':'unused.h'}]
        incremental=[{'type':'MISSING','target':'main.o','dependency':'config.h'},
                     {'type':'REDUNDANT','target':'main.o','dependency':'unused.h'}]
        self.assertEqual(pipeline.normalized(full), pipeline.normalized(incremental))


if __name__=='__main__':unittest.main()
