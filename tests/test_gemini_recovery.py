import json

import httpx
import pytest

from conftest import CONTENT, SUMMARY
from test_llm import gemini_config, gemini_success, summary
from utility_scripts.contracts import KBError, load_config
from utility_scripts.llm import Gemini, OpenAI, create_provider, maximum_requests, retry_delay


@pytest.mark.parametrize('status', [404, 503])
def test_gemini_discovers_available_reviewed_model_and_remembers_it(repo, monkeypatch, status):
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
    seen = []
    cfg = gemini_config(repo)
    def handler(request):
        assert request.headers['Authorization'] == 'Bearer test-key'
        if request.method == 'GET':
            assert str(request.url) == Gemini.models_endpoint
            seen.append('list')
            return httpx.Response(200, json={'data': [
                {'id': 'gemini-unreviewed-preview'}, {'id': 'models/gemini-3.5-flash-lite'}]})
        model = json.loads(request.content)['model']
        seen.append(model)
        return httpx.Response(status) if model == 'gemini-3.8-flash' else gemini_success(summary())
    client = create_provider(repo, cfg, transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        assert client.summarize('protein', CONTENT)['summary'] == SUMMARY
        assert client.provenance('summary')['model'] == 'gemini-3.5-flash-lite'
        client.summarize('protein', CONTENT)
        assert seen == ['gemini-3.8-flash', 'list', 'gemini-3.5-flash-lite', 'gemini-3.5-flash-lite']
        assert client.requests == 4
        assert cfg['model'] == 'gemini-3.8-flash'
    finally:
        client.close()


@pytest.mark.parametrize('listing', ['error', 'malformed', 'unknown', 'empty', 'transport'])
def test_discovery_failure_is_bounded_sanitized_and_keeps_known_model(repo, monkeypatch, caplog, listing):
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
    seen = []
    def handler(request):
        seen.append(request.method)
        if request.method == 'GET':
            if listing == 'error':
                return httpx.Response(403, text='secret-body')
            if listing == 'malformed':
                return httpx.Response(200, text='secret-body')
            if listing == 'transport':
                raise httpx.ReadTimeout('secret-body', request=request)
            return httpx.Response(200, json={'data': [{'id': 'unknown-model'}] if listing == 'unknown' else []})
        assert json.loads(request.content)['model'] == 'gemini-3.8-flash'
        return httpx.Response(503, text='secret-body')
    client = Gemini(repo, gemini_config(repo), transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        with pytest.raises(KBError, match='503') as error:
            client.summarize('protein', CONTENT)
        assert seen == ['POST', 'GET', 'POST', 'POST']
        assert client.requests == 4
        assert 'secret-body' not in str(error.value) + caplog.text
    finally:
        client.close()


def test_discovery_and_recovery_share_batch_budget(repo, monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
    cfg = gemini_config(repo)
    cfg['max_api_requests'] = 2
    seen = []
    def handler(request):
        seen.append(request.method)
        if request.method == 'GET':
            return httpx.Response(200, json={'data': [{'id': 'gemini-3.5-flash-lite'}]})
        return httpx.Response(503)
    client = create_provider(repo, cfg, transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        with pytest.raises(KBError, match='budget exhausted'):
            client.summarize('protein', CONTENT)
        assert seen == ['POST', 'GET']
        assert client.requests == 2
    finally:
        client.close()


def test_failed_run_scenario_recovers_relationships_on_another_model(repo, monkeypatch):
    from utility_scripts.ingest import run
    from utility_scripts.storage import load_collection
    monkeypatch.setenv('OPENAI_API_KEY', 'invalid-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
    (repo / 'markdown/first.md').write_text(CONTENT)
    (repo / 'markdown/second.md').write_text(CONTENT + '\nMore notes.\n')
    seen = []
    def handler(request):
        if str(request.url) == OpenAI.endpoint:
            return httpx.Response(401)
        if request.method == 'GET':
            seen.append('list')
            return httpx.Response(200, json={'data': [{'id': 'gemini-3.5-flash-lite'}]})
        body = json.loads(request.content)
        task = body['response_format']['json_schema']['name']
        seen.append((task, body['model']))
        if task == 'summary':
            return gemini_success(summary())
        if body['model'] == 'gemini-3.8-flash':
            return httpx.Response(503)
        payload = json.loads(body['messages'][1]['content'])
        return gemini_success({'source': payload['source']['document_id'], 'target': payload['target']['document_id'],
                               'related': True, 'rationale': 'Both documents study protein dynamics.'})
    real_client = httpx.Client
    monkeypatch.setattr('utility_scripts.llm.httpx.Client',
                        lambda **kwargs: real_client(**{**kwargs, 'transport': httpx.MockTransport(handler)}))
    monkeypatch.setattr('utility_scripts.llm.retry_delay', lambda *_: 0)
    report = run(repo)
    records, relationships = load_collection(repo)
    assert report['api_requests'] == 6
    assert all(record['generation']['model'] == 'gemini-3.8-flash' for record in records.values())
    assert relationships['edges'][0]['generation']['model'] == 'gemini-3.5-flash-lite'
    assert seen.count('list') == 1
    assert run(repo, 'validate')['valid']


def test_transient_delays_honor_retry_after_and_stay_bounded(monkeypatch):
    monkeypatch.setattr('utility_scripts.llm.random.uniform', lambda *_: 0.5)
    assert retry_delay(httpx.Response(503), 0) == 5.5
    assert retry_delay(httpx.Response(503), 1) == 10.5
    assert retry_delay(httpx.Response(429, headers={'Retry-After': '30'}), 0) == 30
    assert retry_delay(httpx.Response(503, headers={'Retry-After': '3600'}), 0) == 60
    assert retry_delay(httpx.Response(503, headers={'Retry-After': 'garbage'}), 0) == 5.5
    monkeypatch.setattr('utility_scripts.llm.time.time', lambda: 0)
    assert retry_delay(httpx.Response(503, headers={'Retry-After': 'Thu, 01 Jan 1970 00:00:45 GMT'}), 0) == 45
    assert maximum_requests(0) == 0
    assert maximum_requests(23) == 139


def test_alternate_model_can_be_configured_explicitly(repo):
    cfg = gemini_config(repo)
    cfg['model'] = 'gemini-3.5-flash-lite'
    (repo / 'config/ingestion.json').write_text(json.dumps(cfg))
    assert load_config(repo)['model'] == cfg['model']
