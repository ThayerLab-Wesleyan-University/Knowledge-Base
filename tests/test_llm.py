import json

import httpx
import pytest

from conftest import CONTENT, KEYWORDS, SUMMARY
from utility_scripts.contracts import KBError, load_config, validate_relationship, validate_summary
from utility_scripts.llm import OpenAI


def success(value):
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


def test_no_key_and_no_automatic_provider_fallback(repo, monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    with pytest.raises(KBError, match='OPENAI_API_KEY'):
        OpenAI(repo, load_config(repo))
    cfg = load_config(repo)
    cfg['provider'] = 'gemini'
    (repo / 'config/ingestion.json').write_text(json.dumps(cfg))
    with pytest.raises(KBError):
        load_config(repo)


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
        assert json.loads(requests[1]['input'])['previous_output'] == bad
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
