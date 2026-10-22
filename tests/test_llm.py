import json

import httpx
import pytest

from conftest import CONTENT, KEYWORDS, SUMMARY
from utility_scripts.contracts import KBError, load_config, validate_relationship, validate_summary
from utility_scripts.llm import OpenAI, Gemini, create_provider


def wire_summary(value):
    if isinstance(value, dict) and 'summary' in value:
        value = dict(value)
        value['summary_words'] = value.pop('summary').split() if value['sufficient'] else None
    return value


def success(value):
    value = wire_summary(value)
    return httpx.Response(200, json={'status': 'completed', 'output': [
        {'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(value)}]}]})


def summary():
    return {'sufficient': True, 'title': '', 'summary': SUMMARY, 'keywords': KEYWORDS[:]}


def test_structured_request_and_validation_retry(repo, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-only-key')
    requests = []
    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        assert str(request.url) == 'https://api.openai.com/v1/responses'
        assert body['store'] is False
        assert body['text']['format']['strict'] is True
        assert body['text']['format']['type'] == 'json_schema'
        assert 'untrusted document data' in body['instructions']
        assert json.loads(body['input'])['document'] == CONTENT
        value = summary()
        if len(requests) == 1:
            value['summary'] = 'too short'
        return success(value)
    client = OpenAI(repo, load_config(repo), transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        assert client.summarize('protein', CONTENT)['summary'] == SUMMARY
        assert client.requests == 2
        assert 'prior attempt' in requests[1]['instructions']
    finally:
        client.close()


@pytest.mark.parametrize('kind,expected', [('rate_limit', 3), ('timeout', 3), ('malformed', 3),
                                         ('refusal', 3), ('incomplete', 3), ('authentication', 1)])
def test_bounded_failures_and_no_response_body_leak(repo, monkeypatch, kind, expected):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-only-key')
    def handler(request):
        if kind == 'timeout':
            raise httpx.ReadTimeout('secret-body', request=request)
        if kind == 'rate_limit':
            return httpx.Response(429, text='secret-body')
        if kind == 'authentication':
            return httpx.Response(401, text='secret-body')
        if kind == 'malformed':
            return httpx.Response(200, text='secret-body')
        if kind == 'incomplete':
            return httpx.Response(200, json={'status': 'incomplete'})
        return httpx.Response(200, json={'status': 'completed', 'output': [
            {'type': 'message', 'content': [{'type': 'refusal', 'refusal': 'secret-body'}]}]})
    client = OpenAI(repo, load_config(repo), transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        with pytest.raises(KBError) as result:
            client.summarize('protein', CONTENT)
        assert 'secret-body' not in str(result.value)
        assert client.requests == expected
    finally:
        client.close()


def test_global_budget_is_shared_across_requests(repo, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-only-key')
    cfg = load_config(repo)
    cfg['max_api_requests'] = 1
    client = OpenAI(repo, cfg, transport=httpx.MockTransport(lambda _: success(summary())), sleep=lambda _: None)
    try:
        client.summarize('protein', CONTENT)
        with pytest.raises(KBError, match='budget exhausted'):
            client.summarize('protein', CONTENT)
        assert client.requests == 1
    finally:
        client.close()


def test_no_key_and_mismatched_provider_model(repo, monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    with pytest.raises(KBError, match='OPENAI_API_KEY'):
        OpenAI(repo, load_config(repo))
    cfg = load_config(repo)
    cfg['provider'] = 'gemini'
    (repo / 'config/ingestion.json').write_text(json.dumps(cfg))
    with pytest.raises(KBError):
        load_config(repo)


def gemini_config(repo):
    cfg = load_config(repo)
    cfg.update(provider='gemini', model='gemini-3.8-flash')
    (repo / 'config/ingestion.json').write_text(json.dumps(cfg))
    return load_config(repo)


def gemini_success(value):
    return httpx.Response(200, json={'choices': [{'finish_reason': 'stop',
        'message': {'role': 'assistant', 'content': json.dumps(wire_summary(value))}}]})


def test_gemini_routing_structured_output_and_repair(repo, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'unused-openai-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    requests = []
    def handler(request):
        assert str(request.url) == Gemini.endpoint
        assert request.headers['Authorization'] == 'Bearer gemini-test-key'
        body = json.loads(request.content)
        requests.append(body)
        assert body['model'] == 'gemini-3.8-flash'
        assert body['response_format']['json_schema']['strict'] is True
        assert body['max_tokens'] == 2048
        assert 'untrusted document data' in body['messages'][0]['content']
        payload = json.loads(body['messages'][1]['content'])
        assert payload['document'] == CONTENT
        value = summary()
        if len(requests) == 1:
            value['summary'] = 'too short'
        else:
            assert payload['previous_output']['summary_words'] == ['too', 'short']
        return gemini_success(value)
    client = create_provider(repo, gemini_config(repo), transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        assert client.summarize('protein', CONTENT)['summary'] == SUMMARY
        assert client.requests == 2
        assert client.provenance('summary')['provider'] == 'gemini'
    finally:
        client.close()


def test_gemini_requires_its_own_key(repo, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'unused-openai-key')
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    with pytest.raises(KBError, match='GEMINI_API_KEY'):
        Gemini(repo, gemini_config(repo))


@pytest.mark.parametrize('kind,expected', [('rate_limit', 3), ('length', 3), ('refusal', 3),
                                         ('malformed', 3), ('authentication', 1)])
def test_gemini_bounded_failures(repo, monkeypatch, kind, expected):
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    def handler(request):
        if kind in ('rate_limit', 'authentication'):
            return httpx.Response(429 if kind == 'rate_limit' else 401, text='secret-body')
        if kind == 'malformed':
            return httpx.Response(200, text='secret-body')
        return httpx.Response(200, json={'choices': [{
            'finish_reason': 'length' if kind == 'length' else 'stop',
            'message': {'refusal': 'secret-body', 'content': None}}]})
    client = Gemini(repo, gemini_config(repo), transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        with pytest.raises(KBError) as result:
            client.summarize('protein', CONTENT)
        assert 'secret-body' not in str(result.value)
        assert client.requests == expected
    finally:
        client.close()


def test_gemini_pipeline_uses_config_and_preserves_existing_provenance(repo, provider, monkeypatch):
    from utility_scripts.ingest import run
    (repo / 'markdown/first.md').write_text(CONTENT)
    run(repo, provider_factory=provider)
    original = {p: p.read_bytes() for p in (repo / 'KG/node_contents').glob('*/metadata.json')}
    cfg = gemini_config(repo)
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    (repo / 'markdown/second.md').write_text(CONTENT + '\nAdditional research notes.\n')
    def handler(request):
        assert str(request.url) == Gemini.endpoint
        body = json.loads(request.content)
        if body['response_format']['json_schema']['name'] == 'summary':
            return gemini_success(summary())
        payload = json.loads(body['messages'][1]['content'])
        return gemini_success({'source': payload['source']['document_id'],
            'target': payload['target']['document_id'], 'related': True,
            'rationale': 'Both documents study protein dynamics.'})
    real_client = httpx.Client
    monkeypatch.setattr('utility_scripts.llm.httpx.Client',
                        lambda **kwargs: real_client(**{**kwargs, 'transport': httpx.MockTransport(handler)}))
    run(repo)
    for path, content in original.items():
        assert path.read_bytes() == content
    new_records = [json.loads(p.read_text()) for p in (repo / 'KG/node_contents').glob('*/metadata.json')
                   if p not in original]
    assert len(new_records) == 1
    assert new_records[0]['generation']['provider'] == 'gemini'
    assert new_records[0]['generation']['model'] == cfg['model']
    edges = json.loads((repo / 'KG/relationships.json').read_text())['edges']
    assert len(edges) == 1 and edges[0]['generation']['provider'] == 'gemini'


@pytest.mark.parametrize('change', ['words', 'duplicates', 'empty_keyword', 'sufficient', 'type'])
def test_summary_contract(change):
    value = summary()
    if change == 'words':
        value['summary'] += ' extra'
    elif change == 'duplicates':
        value['keywords'][-1] = '  PROTEIN DYNAMICS  '
    elif change == 'empty_keyword':
        value['keywords'][-1] = ' '
    elif change == 'sufficient':
        value['sufficient'] = False
    else:
        value['sufficient'] = 'true'
    with pytest.raises(KBError):
        validate_summary(value)


def test_relationship_rejects_wrong_ids_and_nonboolean():
    for value in [dict(source='b', target='a', related=True, rationale='Grounded'),
                  dict(source='a', target='b', related='false', rationale='Grounded')]:
        with pytest.raises(KBError):
            validate_relationship(value, 'a', 'b')


def test_word_count_repair_uses_previous_output_and_reports_actual_count(repo, monkeypatch, caplog):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-only-key')
    requests = []
    bad = summary()
    bad['summary'] = 'confidential-document-text ' * 99
    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        return success(bad if len(requests) == 1 else summary())
    client = OpenAI(repo, load_config(repo), transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        client.summarize('protein', CONTENT)
        assert client.requests == 2
        assert 'received 99' in requests[1]['instructions']
        assert json.loads(requests[1]['input'])['previous_output'] == wire_summary(bad)
        assert 'received 99' in caplog.text
        assert 'confidential-document-text' not in caplog.text
    finally:
        client.close()


def test_final_error_preserves_safe_validation_reason(repo, monkeypatch, caplog):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-only-key')
    bad = summary()
    bad['summary'] = 'confidential-document-text ' * 101
    client = OpenAI(repo, load_config(repo), transport=httpx.MockTransport(lambda _: success(bad)), sleep=lambda _: None)
    try:
        with pytest.raises(KBError, match='last error:.*received 101') as result:
            client.summarize('protein', CONTENT)
        assert client.requests == 3
        assert 'confidential-document-text' not in str(result.value) + caplog.text
    finally:
        client.close()


@pytest.mark.parametrize('code', ['insufficient_quota', 'billing_hard_limit_reached', 'credit_balance_exhausted'])
def test_exhausted_billing_does_not_retry(repo, monkeypatch, code):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-only-key')
    transport = httpx.MockTransport(lambda _: httpx.Response(429, json={
        'error': {'code': code, 'message': 'confidential-provider-body'}}))
    client = OpenAI(repo, load_config(repo), transport=transport, sleep=lambda _: pytest.fail('Billing errors must not retry'))
    try:
        with pytest.raises(KBError, match='billing quota exhausted') as result:
            client.summarize('protein', CONTENT)
        assert client.requests == 1
        assert 'confidential-provider-body' not in str(result.value)
    finally:
        client.close()


def test_transport_diagnostics_do_not_echo_exception_secrets(repo, monkeypatch, caplog):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-only-key')
    def handler(request):
        raise httpx.ReadTimeout('secret-api-key and document-body', request=request)
    client = OpenAI(repo, load_config(repo), transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        with pytest.raises(KBError, match='timed out') as result:
            client.summarize('protein', CONTENT)
        assert 'secret-api-key' not in str(result.value) + caplog.text
        assert 'document-body' not in str(result.value) + caplog.text
    finally:
        client.close()


def test_summary_request_enforces_word_array_and_returns_prose(repo, monkeypatch):
    from jsonschema import Draft202012Validator
    monkeypatch.setenv('OPENAI_API_KEY', 'test-only-key')
    def handler(request):
        schema = json.loads(request.content)['text']['format']['schema']
        words_schema = schema['properties']['summary_words']
        assert words_schema['minItems'] == words_schema['maxItems'] == 100
        assert words_schema['items']['pattern'] == r'^\S+$'
        good = wire_summary(summary())
        Draft202012Validator(schema).validate(good)
        for count in (94, 101, 96):
            bad = {**good, 'summary_words': ['word'] * count}
            assert not Draft202012Validator(schema).is_valid(bad)
        return success(good)
    client = OpenAI(repo, load_config(repo), transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        result = client.summarize('protein', CONTENT)
        assert result['summary'] == SUMMARY
        assert 'summary_words' not in result
        assert client.provenance('summary')['prompt_version'] == 'v2'
        assert client.requests == 1
    finally:
        client.close()


@pytest.mark.parametrize('word', ['', 'two words', ' leading', 'trailing ', 'line\nbreak', 'word\n'])
def test_summary_word_items_reject_whitespace(word):
    from utility_scripts.contracts import decode_summary_words
    value = wire_summary(summary())
    value['summary_words'][0] = word
    with pytest.raises(KBError):
        decode_summary_words(value)


def test_summary_words_insufficient_content_is_rejected():
    from utility_scripts.contracts import decode_summary_words
    with pytest.raises(KBError, match='Insufficient'):
        decode_summary_words({'sufficient': False, 'title': '', 'summary_words': None, 'keywords': []})


def test_word_array_ingests_as_plain_text_metadata(repo, monkeypatch):
    from utility_scripts.ingest import run
    from utility_scripts.storage import load_collection
    monkeypatch.setenv('OPENAI_API_KEY', 'test-only-key')
    (repo / 'markdown/test.md').write_text(CONTENT)
    def factory(root, config):
        return OpenAI(root, config, transport=httpx.MockTransport(lambda _: success(summary())), sleep=lambda _: None)
    result = run(repo, provider_factory=factory)
    record = next(iter(load_collection(repo)[0].values()))
    assert record['summary'] == SUMMARY
    assert len(record['summary'].split()) == 100
    assert record['generation']['prompt_version'] == 'v2'
    assert result['api_requests'] == 1
    assert run(repo, 'validate')['valid']


@pytest.mark.parametrize('primary', ['openai', 'gemini'])
@pytest.mark.parametrize('failure,attempts', [('missing_key', 0), ('quota', 1), ('auth', 1),
                                            ('rate_limit', 3), ('timeout', 3), ('invalid', 3)])
def test_automatic_fallback_both_directions(repo, monkeypatch, caplog, primary, failure, attempts):
    cfg = gemini_config(repo) if primary == 'gemini' else load_config(repo)
    monkeypatch.setenv('OPENAI_API_KEY', 'openai-test-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    if failure == 'missing_key':
        monkeypatch.delenv('OPENAI_API_KEY' if primary == 'openai' else 'GEMINI_API_KEY')
    seen = []
    def handler(request):
        name = 'openai' if str(request.url) == OpenAI.endpoint else 'gemini'
        seen.append(name)
        assert request.headers['Authorization'] == f'Bearer {name}-test-key'
        if name == primary:
            if failure == 'quota':
                return httpx.Response(429, json={'error': {'code': 'insufficient_quota', 'message': 'secret-body'}})
            if failure == 'auth':
                return httpx.Response(401, text='secret-body')
            if failure == 'rate_limit':
                return httpx.Response(429, text='secret-body')
            if failure == 'timeout':
                raise httpx.ReadTimeout('secret-body', request=request)
            return httpx.Response(200, text='secret-body')
        return success(summary()) if name == 'openai' else gemini_success(summary())
    client = create_provider(repo, cfg, transport=httpx.MockTransport(handler), sleep=lambda _: None)
    other = 'gemini' if primary == 'openai' else 'openai'
    try:
        assert client.summarize('protein', CONTENT)['summary'] == SUMMARY
        assert seen == [primary] * attempts + [other]
        assert client.requests == attempts + 1
        provenance = client.provenance('summary')
        assert provenance['provider'] == other
        assert provenance['model'] == ('gemini-3.8-flash' if other == 'gemini' else 'gpt-4.1-mini-2025-04-14')
        client.summarize('another protein', CONTENT)
        assert seen == [primary] * attempts + [other, other]
        assert client.requests == attempts + 2
        assert 'secret-body' not in caplog.text
    finally:
        client.close()
    assert all(adapter.client.is_closed for adapter in client.clients.values())


@pytest.mark.parametrize('limit,expected', [(2, ['openai', 'gemini']), (1, ['openai'])])
def test_fallback_cannot_reset_shared_batch_budget(repo, monkeypatch, limit, expected):
    monkeypatch.setenv('OPENAI_API_KEY', 'openai-test-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    cfg = load_config(repo)
    cfg['max_api_requests'] = limit
    seen = []
    def handler(request):
        name = 'openai' if str(request.url) == OpenAI.endpoint else 'gemini'
        seen.append(name)
        return httpx.Response(401) if name == 'openai' else gemini_success(summary())
    client = create_provider(repo, cfg, transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        if limit == 2:
            client.summarize('protein', CONTENT)
        with pytest.raises(KBError, match='budget exhausted'):
            client.summarize('protein', CONTENT)
        assert seen == expected
        assert client.requests == limit
    finally:
        client.close()


def test_both_providers_fail_with_bounded_sanitized_error(repo, monkeypatch, caplog):
    monkeypatch.setenv('OPENAI_API_KEY', 'openai-test-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    client = create_provider(repo, load_config(repo),
        transport=httpx.MockTransport(lambda _: httpx.Response(503, text='secret-body')),
        sleep=lambda _: None)
    try:
        with pytest.raises(KBError, match='Both providers failed') as error:
            client.summarize('protein', CONTENT)
        assert client.requests == 7
        assert 'openai:' in str(error.value) and 'gemini:' in str(error.value)
        assert 'secret-body' not in str(error.value) + caplog.text
    finally:
        client.close()


def test_no_keys_reports_both_required_environment_variables(repo, monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    client = create_provider(repo, load_config(repo))
    try:
        with pytest.raises(KBError, match='Both providers failed') as error:
            client.summarize('protein', CONTENT)
        assert 'OPENAI_API_KEY' in str(error.value) and 'GEMINI_API_KEY' in str(error.value)
        assert client.requests == 0
    finally:
        client.close()


def test_fallback_respects_other_model_limits_and_context_failures(repo, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'openai-test-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    cfg = gemini_config(repo)
    cfg.update(max_output_tokens=65536, model_context_tokens=1048576)
    seen = []
    def handler(request):
        seen.append(str(request.url))
        if str(request.url) == Gemini.endpoint:
            return httpx.Response(401)
        body = json.loads(request.content)
        assert body['max_output_tokens'] == 32768
        return success(summary())
    client = create_provider(repo, cfg, transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        client.summarize('protein', CONTENT)
        assert seen == [Gemini.endpoint, OpenAI.endpoint]
        assert client.provenance('summary')['settings']['max_output_tokens'] == 32768
        assert cfg['max_output_tokens'] == 65536
    finally:
        client.close()
    cfg['model_context_tokens'] = 1
    client = create_provider(repo, cfg, transport=httpx.MockTransport(lambda _: pytest.fail('Oversized request sent')))
    try:
        with pytest.raises(KBError, match='context budget'):
            client.summarize('protein', CONTENT)
        assert list(client.clients) == ['gemini']
        assert client.requests == 0
    finally:
        client.close()


def test_pipeline_records_provider_for_each_successful_operation(repo, monkeypatch):
    from utility_scripts.ingest import run
    from utility_scripts.storage import load_collection
    monkeypatch.setenv('OPENAI_API_KEY', 'openai-test-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    (repo / 'markdown/first.md').write_text(CONTENT)
    (repo / 'markdown/second.md').write_text(CONTENT + '\nAdditional notes.\n')
    def handler(request):
        body = json.loads(request.content)
        if str(request.url) == OpenAI.endpoint:
            if body['text']['format']['name'] == 'summary':
                return success(summary())
            return httpx.Response(401, text='secret-body')
        payload = json.loads(body['messages'][1]['content'])
        return gemini_success({'source': payload['source']['document_id'],
            'target': payload['target']['document_id'], 'related': True,
            'rationale': 'Both documents study protein dynamics.'})
    real_client = httpx.Client
    clients = []
    def mock_client(**kwargs):
        client = real_client(**{**kwargs, 'transport': httpx.MockTransport(handler)})
        clients.append(client)
        return client
    monkeypatch.setattr('utility_scripts.llm.httpx.Client', mock_client)
    report = run(repo)
    records, relationships = load_collection(repo)
    assert report['api_requests'] == 4
    assert all(record['generation']['provider'] == 'openai' for record in records.values())
    assert relationships['edges'][0]['generation']['provider'] == 'gemini'
    assert all(client.is_closed for client in clients)
    assert run(repo, 'validate')['valid']


def test_failed_fallback_leaves_intake_and_collection_unchanged(repo, monkeypatch):
    from utility_scripts.ingest import run
    from utility_scripts.storage import snapshot
    monkeypatch.setenv('OPENAI_API_KEY', 'openai-test-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    (repo / 'markdown/first.md').write_text(CONTENT)
    before = snapshot(repo)
    real_client = httpx.Client
    clients = []
    def mock_client(**kwargs):
        client = real_client(**{**kwargs, 'transport': httpx.MockTransport(lambda _: httpx.Response(401))})
        clients.append(client)
        return client
    monkeypatch.setattr('utility_scripts.llm.httpx.Client', mock_client)
    with pytest.raises(KBError, match='Both providers failed'):
        run(repo)
    assert snapshot(repo) == before
    assert all(client.is_closed for client in clients)


def test_fallback_can_switch_back_when_alternate_later_fails(repo, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'openai-test-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'gemini-test-key')
    seen = []
    def handler(request):
        name = 'openai' if str(request.url) == OpenAI.endpoint else 'gemini'
        seen.append(name)
        if len(seen) in (1, 3):
            return httpx.Response(401)
        return success(summary()) if name == 'openai' else gemini_success(summary())
    client = create_provider(repo, load_config(repo), transport=httpx.MockTransport(handler), sleep=lambda _: None)
    try:
        client.summarize('protein', CONTENT)
        assert client.provenance('summary')['provider'] == 'gemini'
        client.summarize('protein', CONTENT)
        assert client.provenance('summary')['provider'] == 'openai'
        assert seen == ['openai', 'gemini', 'gemini', 'openai']
        assert client.requests == 4
    finally:
        client.close()
