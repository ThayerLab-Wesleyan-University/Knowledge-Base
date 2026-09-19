from pathlib import Path
import shutil

import pytest
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

from utility_scripts.contracts import digest

PROJECT = Path(__file__).resolve().parents[1]
CONTENT = (PROJECT / 'tests/fixtures/protein.md').read_text()
SUMMARY = ' '.join(CONTENT.split()[6:106])
KEYWORDS = ['protein dynamics', 'molecular simulation', 'residue contacts', 'replicas',
            'conformations', 'solvent', 'reproducibility', 'coordinates', 'networks', 'fluctuations']


@pytest.fixture
def repo(tmp_path):
    for folder in ('config', 'prompts'):
        shutil.copytree(PROJECT / folder, tmp_path / folder)
    for folder in ('pdf', 'markdown'):
        (tmp_path / folder).mkdir()
        (tmp_path / folder / 'README.md').write_text('Keep these instructions.\n')
    (tmp_path / 'KG').mkdir()
    (tmp_path / 'README.md').write_text('# Lab\n\n<!-- KG:START -->\nPending\n<!-- KG:END -->\n\nHand-maintained instructions.\n')
    return tmp_path


class FakeProvider:
    def __init__(self, root, config):
        self.config = config
        self.root = root
        self.requests = 0
        self.pairs = []

    def provenance(self, task):
        prompt = (self.root / f'prompts/{task}-v1.txt').read_bytes()
        return {'provider': 'test', 'model': 'offline-fixture', 'prompt_version': 'v1',
                'prompt_sha256': digest(prompt),
                'settings': {'temperature': 0, 'max_output_tokens': 2048}}

    def summarize(self, title, content):
        self.requests += 1
        return {'sufficient': True, 'title': '', 'summary': SUMMARY, 'keywords': KEYWORDS[:]}

    def relate(self, a, b):
        self.requests += 1
        self.pairs.append((a['document_id'], b['document_id']))
        return {'source': a['document_id'], 'target': b['document_id'],
                'related': 'unrelated' not in (a['title'], b['title']),
                'rationale': 'Both records discuss residue contact graphs in molecular simulations.'}

    def close(self):
        pass


@pytest.fixture
def provider():
    instances = []
    def factory(root, config):
        instance = FakeProvider(root, config)
        instances.append(instance)
        return instance
    factory.instances = instances
    return factory


def make_pdf(path, text=CONTENT, *, encrypted=False, blank=False):
    """Small synthetic text PDF built offline, without shipping real publications."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    if not blank:
        font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                                 NameObject('/Subtype'): NameObject('/Type1'),
                                 NameObject('/BaseFont'): NameObject('/Helvetica')})
        page[NameObject('/Resources')] = DictionaryObject({
            NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
        import textwrap
        lines = textwrap.wrap(text, width=85)
        escaped = [line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)') for line in lines]
        stream = DecodedStreamObject()
        stream.set_data(('BT /F1 10 Tf 40 750 Td 14 TL\n' + '\n'.join(f'({line}) Tj T*' for line in escaped) + '\nET').encode())
        page[NameObject('/Contents')] = writer._add_object(stream)
    if encrypted:
        writer.encrypt('test-password')
    writer.write(path)
