import json, tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch,commit

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_independent_known_edges(self):
        r=scan(self.p)
        self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
        self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},{('MISSING','config.h'),('REDUNDANT','unused.h')})

    def test_unchanged_reuses_both_targets(self):
        r=scan(self.p,scan(self.p));self.assertEqual(r['reused'],['main.o','helper.o']);self.assertEqual(r['refreshed'],[])

    def test_include_added_invalidates_cache(self):
        old=scan(self.p)
        (self.p/'main.c').write_text('#include "extra.h"\n'+(self.p/'main.c').read_text());commit(self.p,'new include')
        r=scan(self.p,old)
        self.assertIn(['MISSING','main.o','extra.h'],r['added']);self.assertEqual(len(r['refreshed']),2)

    def test_patch_preserves_redundant_dependency(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertIn('+main.o: main.c unused.h config.h',diff)
        self.assertNotIn('-\tgcc',diff)
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

    def test_old_report_rejected(self):
        r=scan(self.p);r['commit']='0'*40
        with self.assertRaisesRegex(ValueError,'STALE_REPORT'):patch(self.p,r)

    def test_unsafe_dependency_rejected(self):
        r=scan(self.p);r['findings']=[{'type':'MISSING','target':'main.o','dependency':'../outside.h'}]
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):patch(self.p,r)

    def test_unsupported_configuration_rejected(self):
        (self.p/'Makefile').write_text((self.p/'Makefile').read_text().replace('-O0','-include unknown.h'))
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):scan(self.p)

class StudentE8A(unittest.TestCase):
    """Personal case (221900015): a header-level indirect include must
    invalidate the cached actual graph of every target, not only the target
    whose translation unit was edited."""

    def test_indirect_include_in_header_invalidates_cached_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            self.assertEqual(old['actual']['main.o'],['config.h','main.c'])
            self.assertNotIn('extra.h',old['actual']['main.o'])
            header=p/'config.h'
            header.write_text('#include "extra.h"\n'+header.read_text())
            commit(p,'student: indirect include through config.h')
            result=scan(p,old)
            self.assertEqual(result['actual']['main.o'],['config.h','extra.h','main.c'])
            self.assertEqual(result['reused'],[])
            self.assertEqual(set(result['refreshed']),{'main.o','helper.o'})
            self.assertIn(['MISSING','main.o','extra.h'],result['added'])
            self.assertEqual(
                {(x['type'],x['dependency']) for x in result['findings']},
                {('MISSING','config.h'),('MISSING','extra.h'),('REDUNDANT','unused.h')})


class StudentE10A(unittest.TestCase):
    """Personal case (221900015): after a three-level header chain appears,
    the incremental path and the full path must agree on all three sets."""

    def test_transitive_header_chain_matches_full_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            (p/'config.h').write_text('#include "extra.h"\n#define VALUE 1\n')
            (p/'extra.h').write_text('#include "leaf.h"\n')
            (p/'leaf.h').write_text('#define LEAF 7\n')
            commit(p,'student: transitive header chain')
            incremental=scan(p,old)
            full=scan(p)
            for key in ['actual','declared','findings']:
                self.assertEqual(incremental[key],full[key])
            self.assertEqual(incremental['actual']['main.o'],['config.h','extra.h','leaf.h','main.c'])
            self.assertEqual(incremental['reused'],[])
            self.assertEqual(
                {x['dependency'] for x in incremental['findings'] if x['type']=='MISSING'},
                {'config.h','extra.h','leaf.h'})


if __name__=='__main__':unittest.main()
