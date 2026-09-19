"""Regression for cover text stored inside a PDF Form XObject."""
import io

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DecodedStreamObject, DictionaryObject, NameObject, NumberObject

from utility_scripts.contracts import KBError
from utility_scripts.pdf2md import convert_pdf

CONFIG = {'max_pdf_pages': 100, 'max_pdf_page_stream_bytes': 1_000_000}


def form_cover_pdf():
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                             NameObject('/Subtype'): NameObject('/Type1'),
                             NameObject('/BaseFont'): NameObject('/Helvetica')})
    form = DecodedStreamObject()
    form.set_data(b'BT /F1 12 Tf 40 700 Td (Thesis cover title) Tj ET')
    form.update({NameObject('/Type'): NameObject('/XObject'),
                 NameObject('/Subtype'): NameObject('/Form'),
                 NameObject('/BBox'): ArrayObject([NumberObject(n) for n in (0, 0, 612, 792)]),
                 NameObject('/Resources'): DictionaryObject({NameObject('/Font'): DictionaryObject({
                     NameObject('/F1'): writer._add_object(font)})})})
    page[NameObject('/Resources')] = DictionaryObject({NameObject('/XObject'): DictionaryObject({
        NameObject('/Cover'): writer._add_object(form)})})
    stream = DecodedStreamObject()
    stream.set_data(b'q /Cover Do Q')
    page[NameObject('/Contents')] = writer._add_object(stream)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def test_form_cover_falls_back_to_plain_extraction():
    data = form_cover_pdf()
    page = PdfReader(io.BytesIO(data)).pages[0]
    assert not page.extract_text(extraction_mode='layout').strip()
    text, provenance = convert_pdf(data, CONFIG)
    assert 'Thesis cover title' in text
    assert '## Page 1' in text
    assert provenance['tool'] == 'pypdf-layout-with-plain-fallback'


def test_truly_textless_page_still_fails():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    data = io.BytesIO()
    writer.write(data)
    with pytest.raises(KBError, match='page 1 has no extractable text'):
        convert_pdf(data.getvalue(), CONFIG)
