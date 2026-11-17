## e11-a-01  SUCCEEDED
- base `39771bcb4abeb7221902856998f0c140904abd1b` target `339584a4669ff67ac8180d2fe5d28d4c006595a0`
- job `job-e80775b25697455088a402d507fa8d90` trace `trace-d3c94f452a8d47d6a5425fc8cb058800`
- refreshed ['main.o', 'helper.o'] reused []
- findings [['MISSING', 'main.o', 'config.h'], ['MISSING', 'main.o', 'extra.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- baseline [['MISSING', 'main.o', 'config.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- stages [('full-check', '22319170c6b9'), ('incremental-check', 'fcbb6406501a')]

## e11-a-02  SUCCEEDED
- base `339584a4669ff67ac8180d2fe5d28d4c006595a0` target `5ad61bd0ae19836c808af21bf2b0073c0c5ff9ef`
- job `job-ee5740e0023f4b73ba30d34543078c7f` trace `trace-51d027ee6c864f3cb9ab2b3de1d875fe`
- refreshed [] reused ['main.o', 'helper.o']
- findings [['MISSING', 'main.o', 'config.h'], ['MISSING', 'main.o', 'extra.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- baseline [['MISSING', 'main.o', 'config.h'], ['MISSING', 'main.o', 'extra.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- stages [('full-check', '1cfb91f078e2'), ('incremental-check', '464bbb6f17ac')]

## e11-b-02  SUCCEEDED
- base `39771bcb4abeb7221902856998f0c140904abd1b` target `339584a4669ff67ac8180d2fe5d28d4c006595a0`
- job `job-4a530a230cc84e059c8b0bfb3bc2d6eb` trace `trace-cdd21531f8de4133b4c53338d1f78596`
- draft SUCCEEDED attempts [[1, 1, 'MISSING_MAKE'], [2, 0, None]] elapsed_ms 121480
- verify exit 0 expected 1 actual '1\n' match True
- edits [{'target': 'main.o', 'dependency': 'config.h', 'style': 'direct'}, {'target': 'main.o', 'dependency': 'extra.h', 'style': 'direct'}]
- recheck findings [['REDUNDANT', 'main.o', 'unused.h']]
- validation {'accepted': True, 'checks': {'patch_applies': True, 'build': True, 'test': True, 'header_change': True, 'no_missing': True}, 'error': None, 'rollback': False, 'source_unchanged': False}
- patched makefile sha `0f81bca34c5eba59329155cda11ac564ea0d05abc646badbb8ce831814805db0`
- stages [('draft', '140b1fbc6ed7'), ('fixed-md', 'cb8963bc4f15'), ('repair', 'cd0b70f8c80c'), ('recheck', '1b825738f05b')]

## e11-b-macro-01  SUCCEEDED
- base `df933042aed69ca04c43d8c8df1906e045863361` target `0d0c8e1dbad14c1aecee4947c04de891700f9f49`
- job `job-c098aa06412546bb8026a1c98fb3d2f0` trace `trace-b58918967e21427d861e2a1f59710722`
- draft SUCCEEDED attempts [[1, 1, 'MISSING_MAKE'], [2, 0, None]] elapsed_ms 118617
- verify exit 0 expected 1 actual '1\n' match True
- edits [{'target': 'main.o', 'dependency': 'config.h', 'style': 'macro'}, {'target': 'main.o', 'dependency': 'extra.h', 'style': 'macro'}]
- recheck findings [['REDUNDANT', 'main.o', 'unused.h']]
- validation {'accepted': True, 'checks': {'patch_applies': True, 'build': True, 'test': True, 'header_change': True, 'no_missing': True}, 'error': None, 'rollback': False, 'source_unchanged': False}
- patched makefile sha `864dc49380fb254ad95c92f9be84df618b03ad3757f7eb1cfc4da40e7778d5f5`
- stages [('draft', '84d7197c47e7'), ('fixed-md', 'd5ed74a7ad77'), ('repair', '9b52df2cc58c'), ('recheck', '0937576a4f2b')]

## e11-b-stale-01  FAILED
- base `39771bcb4abeb7221902856998f0c140904abd1b` target `339584a4669ff67ac8180d2fe5d28d4c006595a0`
- job `job-48c846a3a4b94cf3bcb5cc9304366b6f` trace `trace-478b6c44463a4bc49ab46d532c6c3a31`
- error `{'code': 'STALE_REPORT', 'message': 'Report belongs to another commit'}`
- draft SUCCEEDED attempts [[1, 1, 'MISSING_MAKE'], [2, 0, None]] elapsed_ms 844
- verify exit 0 expected 1 actual '1\n' match True
- stages [('draft', 'aba0a89efd87')]

## e12-01  SUCCEEDED
- base `39771bcb4abeb7221902856998f0c140904abd1b` target `339584a4669ff67ac8180d2fe5d28d4c006595a0`
- job `job-c4408a0deeec47e2a6f33b50744c85c4` trace `trace-efa0103231dc47c9b7cbe130d0f5f032`
- refreshed ['main.o', 'helper.o'] reused []
- findings [['MISSING', 'main.o', 'config.h'], ['MISSING', 'main.o', 'extra.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- baseline [['MISSING', 'main.o', 'config.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- draft SUCCEEDED attempts [[1, 1, 'MISSING_MAKE'], [2, 0, None]] elapsed_ms 996
- verify exit 0 expected 1 actual '1\n' match True
- edits [{'target': 'main.o', 'dependency': 'config.h', 'style': 'direct'}, {'target': 'main.o', 'dependency': 'extra.h', 'style': 'direct'}]
- recheck findings [['REDUNDANT', 'main.o', 'unused.h']]
- validation {'accepted': True, 'checks': {'patch_applies': True, 'build': True, 'test': True, 'header_change': True, 'no_missing': True}, 'error': None, 'rollback': False, 'source_unchanged': False}
- patched makefile sha `0f81bca34c5eba59329155cda11ac564ea0d05abc646badbb8ce831814805db0`
- stages [('draft', 'b8701e09501d'), ('full-check', '30f43b260638'), ('incremental-check', 'a4361c94f7eb'), ('repair', '37df98f0004b'), ('recheck', 'a739cbabcb4d')]

## e11-real-c1-01  SUCCEEDED
- base `67bd1940dba544c1be01eefea87886b6cfade1af` target `ec4279f8b57e2d1b848fdcd08c7108d5971a9eca`
- job `job-07ff90537fb64adaaff69db955ee28aa` trace `trace-5546a3d9c17940a4892810bbeecbcc01`
- refreshed [] reused ['main.o', 'helper.o']
- findings [['MISSING', 'main.o', 'config.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- baseline [['MISSING', 'main.o', 'config.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- stages [('full-check', '62ef31d8731f'), ('incremental-check', '00afb1fcb6d7')]

## e11-real-c2-01  SUCCEEDED
- base `67bd1940dba544c1be01eefea87886b6cfade1af` target `9560d1a1c98d1769b848e851c4c73ef4ff9e5de8`
- job `job-91d48136224841a28dac2e2027f738a9` trace `trace-968d97e28f5a484cb914e50914232b2f`
- refreshed ['main.o', 'helper.o'] reused []
- findings [['MISSING', 'main.o', 'config.h'], ['MISSING', 'main.o', 'extra.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- baseline [['MISSING', 'main.o', 'config.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- stages [('full-check', '1a261fd92bb4'), ('incremental-check', 'cf5f332971fe')]

## e12-real-01  SUCCEEDED
- base `67bd1940dba544c1be01eefea87886b6cfade1af` target `9560d1a1c98d1769b848e851c4c73ef4ff9e5de8`
- job `job-4a7b02f4bbf74fc1a6b9c8c5d66d1338` trace `trace-e8144c59c9914e6991aae7a28cef5bb6`
- refreshed ['main.o', 'helper.o'] reused []
- findings [['MISSING', 'main.o', 'config.h'], ['MISSING', 'main.o', 'extra.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- baseline [['MISSING', 'main.o', 'config.h'], ['REDUNDANT', 'main.o', 'unused.h']]
- draft SUCCEEDED attempts [[1, 1, 'MISSING_MAKE'], [2, 0, None]] elapsed_ms 118406
- verify exit 0 expected 1 actual '1\n' match True
- edits [{'target': 'main.o', 'dependency': 'config.h', 'style': 'direct'}, {'target': 'main.o', 'dependency': 'extra.h', 'style': 'direct'}]
- recheck findings [['REDUNDANT', 'main.o', 'unused.h']]
- validation {'accepted': True, 'checks': {'patch_applies': True, 'build': True, 'test': True, 'header_change': True, 'no_missing': True}, 'error': None, 'rollback': False, 'source_unchanged': False}
- patched makefile sha `0f81bca34c5eba59329155cda11ac564ea0d05abc646badbb8ce831814805db0`
- stages [('draft', '9bd456734127'), ('full-check', '4d16aa50e067'), ('incremental-check', 'e6afb5c1f1bc'), ('repair', '6ede934ef8cf'), ('recheck', '2ec49c4ad2a3')]
