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
    """Student addition (241880335): an indirect include inside a header
    invalidates the cached graph for every target, even the one whose own
    translation unit did not change."""

    def test_indirect_include_in_header_invalidates_old_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            self.assertNotIn('extra.h',old['actual']['main.o'])
            header=p/'config.h'
            header.write_text('#include "extra.h"\n'+header.read_text())
            commit(p,'student: indirect include through config.h')
            result=scan(p,old)
            self.assertNotIn('extra.h',old['actual']['main.o'])
            self.assertIn('extra.h',result['actual']['main.o'])
            self.assertEqual(result['actual']['main.o'],['config.h','extra.h','main.c'])
            self.assertEqual(result['reused'],[])
            self.assertEqual(set(result['refreshed']),{'main.o','helper.o'})
            self.assertIn(['MISSING','main.o','extra.h'],result['added'])


class StudentE9A(unittest.TestCase):
    """Student addition (241880335): E9 core claim — a declaration-only change
    reuses the actual graph because recipes are untouched, yet ``resolved``
    must still be recomputed against the freshly parsed declarations.

    The existing suite checks ``added`` once (direct include) but never walks a
    two-step C2->C3 chain, so nothing pins down that ``resolved`` accumulates
    exactly the MD entries that the repaired declaration now covers while the
    untouched RD survives.
    """

    def test_declaration_repair_reuses_graph_and_resolves_exactly_two_md(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            c0=scan(p)
            self.assertEqual(
                {(x['type'],x['target'],x['dependency']) for x in c0['findings']},
                {('MISSING','main.o','config.h'),('REDUNDANT','main.o','unused.h')})

            src=p/'main.c'
            src.write_text('#include "extra.h"\n'+src.read_text())
            commit(p,'student: C2 include')
            c2=scan(p,c0)
            self.assertEqual(set(c2['refreshed']),{'main.o','helper.o'})
            self.assertEqual(c2['resolved'],[])
            self.assertIn(['MISSING','main.o','extra.h'],c2['added'])

            makefile=p/'Makefile'
            makefile.write_text(
                makefile.read_text().replace('main.c unused.h','main.c unused.h config.h extra.h'))
            commit(p,'student: C3 repair declarations')
            c3=scan(p,c2)

            self.assertEqual(c3['key'],c2['key'],
                'Declaration-only change touches no recipe line, so the cache key must stay equal')
            self.assertEqual(c3['reused'],['main.o','helper.o'])
            self.assertEqual(c3['refreshed'],[])
            self.assertEqual(c3['actual'],c2['actual'])
            self.assertEqual(c3['added'],[])
            self.assertEqual(sorted(c3['resolved']),
                [['MISSING','main.o','config.h'],['MISSING','main.o','extra.h']])
            self.assertEqual(c3['findings'],
                [{'type':'REDUNDANT','target':'main.o','dependency':'unused.h'}])
            self.assertNotIn('config.h',c3['declared']['helper.o'])


class StudentE10A(unittest.TestCase):
    """Student addition (241880335): E10 asks for one extra scenario with a
    full dependency expectation, repeated five times.

    The scenario pins the exact granularity of the cache key. ``key`` only
    collects lines whose first non-space character is ``#``, so a C comment
    inside a header never reaches the preprocessor and must NOT invalidate the
    graph, while adding a real ``#define`` MUST invalidate it even though the
    include set is unchanged. The second half also shows the documented cost of
    the coarse key: refresh happens with no change in actual/declared/findings,
    and the five repeats prove the conservative result still equals a full scan.
    """

    def test_comment_reuses_but_new_directive_refreshes_five_times(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            base=scan(p)
            self.assertEqual(base['actual']['main.o'],['config.h','main.c'])

            header=p/'config.h'
            header.write_text('/* student: documentation only */\n'+header.read_text())
            commit(p,'student: comment only')
            after_comment=scan(p,base)

            self.assertEqual(after_comment['key'],base['key'],
                'A C comment is not a preprocessing directive, so the key must stay equal')
            self.assertEqual(after_comment['reused'],['main.o','helper.o'])
            self.assertEqual(after_comment['refreshed'],[])
            self.assertEqual(after_comment['actual'],base['actual'])
            self.assertEqual(after_comment['findings'],base['findings'])

            header.write_text('#define UNUSED_MACRO 1\n'+header.read_text())
            commit(p,'student: new directive')
            previous=after_comment
            repeats=[]
            for repeat in range(1,6):
                inc=scan(p,previous)
                full=scan(p)
                equal=all(inc[k]==full[k] for k in ['actual','declared','findings'])
                repeats.append((repeat,equal,tuple(inc['reused']),tuple(inc['refreshed'])))
                self.assertTrue(equal,f'directive case repeat {repeat} differs from full scan')
                self.assertEqual(inc['reused'],[])
                self.assertEqual(set(inc['refreshed']),{'main.o','helper.o'})
                self.assertNotEqual(inc['key'],previous['key'],
                    'A new #define must change the cache key')

            self.assertEqual(len(repeats),5)
            self.assertEqual({r[1] for r in repeats},{True},
                'All five repeats must agree with the full scan')
            self.assertEqual({r[2] for r in repeats},{()},
                'Every repeat must show zero reuse')
            self.assertEqual({r[3] for r in repeats},{('main.o','helper.o')},
                'Refresh order is deterministic: both targets, main.o first')



class Student241880515DependencyReplacement(unittest.TestCase):
    """Replace a transitive dependency without changing the edge count."""

    def test_transitive_leaf_replacement_removes_old_edge(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'sample'
            fixture(p)
            original = scan(p)

            # Both leaf files exist throughout the replacement.
            # Only the include directive changes in the second phase.
            (p / 'leaf_a.h').write_text('#define LEAF_A 7\n')
            (p / 'leaf_b.h').write_text('#define LEAF_B 9\n')
            (p / 'config.h').write_text(
                '#include "extra.h"\n#define VALUE 1\n')
            (p / 'extra.h').write_text(
                '#include "leaf_a.h"\n#define EXTRA 0\n')
            commit(p, '241880515: add transitive leaf_a dependency')

            old = scan(p, original)
            self.assertEqual(old['actual'], {
                'main.o': ['config.h', 'extra.h', 'leaf_a.h', 'main.c'],
                'helper.o': ['helper.c'],
            })
            self.assertEqual(
                {(f['type'], f['target'], f['dependency'])
                 for f in old['findings']},
                {
                    ('MISSING', 'main.o', 'config.h'),
                    ('MISSING', 'main.o', 'extra.h'),
                    ('MISSING', 'main.o', 'leaf_a.h'),
                    ('REDUNDANT', 'main.o', 'unused.h'),
                })
            self.assertEqual(old['reused'], [])
            self.assertEqual(set(old['refreshed']), {'main.o', 'helper.o'})

            # Keep leaf_a.h on disk: it becomes unused, not deleted.
            (p / 'extra.h').write_text(
                '#include "leaf_b.h"\n#define EXTRA 0\n')
            commit(p, '241880515: replace transitive leaf_a with leaf_b')

            result = scan(p, old)
            full = scan(p)

            self.assertEqual(result['actual'], {
                'main.o': ['config.h', 'extra.h', 'leaf_b.h', 'main.c'],
                'helper.o': ['helper.c'],
            })
            self.assertEqual(result['declared'], {
                'main.o': ['main.c', 'unused.h'],
                'helper.o': ['helper.c'],
            })
            self.assertEqual(
                {(f['type'], f['target'], f['dependency'])
                 for f in result['findings']},
                {
                    ('MISSING', 'main.o', 'config.h'),
                    ('MISSING', 'main.o', 'extra.h'),
                    ('MISSING', 'main.o', 'leaf_b.h'),
                    ('REDUNDANT', 'main.o', 'unused.h'),
                })
            self.assertEqual(
                result['added'], [['MISSING', 'main.o', 'leaf_b.h']])
            self.assertEqual(
                result['resolved'], [['MISSING', 'main.o', 'leaf_a.h']])
            self.assertEqual(result['reused'], [])
            self.assertEqual(set(result['refreshed']), {'main.o', 'helper.o'})

            for key in ['actual', 'declared', 'findings']:
                self.assertEqual(result[key], full[key], key)

            # The historical report must remain unchanged.
            self.assertIn('leaf_a.h', old['actual']['main.o'])
            self.assertNotIn('leaf_b.h', old['actual']['main.o'])


if __name__=='__main__':unittest.main()

class StudentE8A221900015(unittest.TestCase):
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


class StudentE10A221900015(unittest.TestCase):
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

class StudentE9A221900015(unittest.TestCase):
    """Personal case (221900015) for E9: replay the track-A mutation chain
    (body -> include -> declaration) and assert that only the include step
    invalidates the cached graph, while the declaration step keeps the graph
    and re-derives every finding from the new Makefile."""

    def test_body_include_declaration_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            c0=scan(p)
            self.assertEqual(c0['findings'],[
                {'type':'MISSING','target':'main.o','dependency':'config.h'},
                {'type':'REDUNDANT','target':'main.o','dependency':'unused.h'}])

            main=p/'main.c'
            main.write_text(main.read_text().replace('return 0;}','return 1;}'))
            commit(p,'student: body change only')
            c1=scan(p,c0)
            self.assertEqual(c1['key'],c0['key'])
            self.assertEqual(c1['reused'],['main.o','helper.o'])
            self.assertEqual(c1['refreshed'],[])
            self.assertEqual(c1['findings'],c0['findings'])

            main.write_text('#include "extra.h"\n'+main.read_text())
            commit(p,'student: include change')
            c2=scan(p,c1)
            self.assertNotEqual(c2['key'],c1['key'])
            self.assertEqual(c2['reused'],[])
            self.assertEqual(set(c2['refreshed']),{'main.o','helper.o'})
            self.assertEqual(c2['actual']['main.o'],['config.h','extra.h','main.c'])
            self.assertEqual(c2['added'],[['MISSING','main.o','extra.h']])

            make=p/'Makefile'
            make.write_text(make.read_text().replace(
                'main.o: main.c unused.h','main.o: main.c unused.h config.h extra.h'))
            commit(p,'student: repair declarations')
            c3=scan(p,c2)
            self.assertEqual(c3['key'],c2['key'])
            self.assertEqual(c3['reused'],['main.o','helper.o'])
            self.assertEqual(c3['refreshed'],[])
            self.assertEqual(c3['actual'],c2['actual'])
            self.assertEqual(c3['resolved'],[
                ['MISSING','main.o','config.h'],
                ['MISSING','main.o','extra.h']])
            self.assertEqual(c3['findings'],[
                {'type':'REDUNDANT','target':'main.o','dependency':'unused.h'}])

