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


def test_deletion_is_manual_main_only_and_serialized_with_ingestion():
    text = (PROJECT / '.github/workflows/delete-document.yml').read_text()
    deletion = yaml.load(text, Loader=yaml.BaseLoader)
    ingest = yaml.load((PROJECT / '.github/workflows/ingest.yml').read_text(), Loader=yaml.BaseLoader)
    assert set(deletion['on']) == {'workflow_dispatch'}
    assert deletion['on']['workflow_dispatch']['inputs']['document_id']['required'] == 'true'
    assert deletion['permissions'] == {'contents': 'write'}
    assert deletion['concurrency'] == ingest['concurrency']
    job = deletion['jobs']['delete']
    assert job['if'] == "github.ref == 'refs/heads/main'"
    assert job['steps'][0]['with']['ref'] == 'main'
    assert 'secrets.' not in text
    for step in job['steps']:
        if 'run' in step:
            assert '${{' not in step['run']
    assert job['steps'][-1]['env']['DOCUMENT_ID'] == '${{ inputs.document_id }}'
    assert job['steps'][-1]['run'].endswith('"$DOCUMENT_ID" --publish')
