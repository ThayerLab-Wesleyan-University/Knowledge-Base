from pathlib import Path
import yaml

PROJECT = Path(__file__).resolve().parents[1]


def test_workflow_permissions_triggers_and_serialization():
    # BaseLoader keeps YAML 1.1 from interpreting GitHub's "on" key as boolean.
    ingest = yaml.load((PROJECT / '.github/workflows/ingest.yml').read_text(), Loader=yaml.BaseLoader)
    tests = yaml.load((PROJECT / '.github/workflows/tests.yml').read_text(), Loader=yaml.BaseLoader)
    assert ingest['permissions'] == {'contents': 'write'}
    assert ingest['concurrency']['cancel-in-progress'] == 'false'
    assert ingest['on']['push']['branches'] == ['main']
    assert ingest['on']['push']['paths'] == ['pdf/**', 'markdown/**']
    assert 'workflow_dispatch' in ingest['on']
    assert ingest['jobs']['ingest']['if'] == "github.ref == 'refs/heads/main'"
    assert ingest['jobs']['ingest']['steps'][0]['with']['ref'] == 'main'
    assert tests['permissions'] == {'contents': 'read'}
    assert 'pull_request' in tests['on'] and 'pull_request_target' not in tests['on']
    assert 'secrets.' not in (PROJECT / '.github/workflows/tests.yml').read_text()
    steps = ingest['jobs']['ingest']['steps']
    assert [step for step in steps if 'env' in step] == [steps[-1]]
    assert steps[-1]['run'].endswith('ingest --publish')
