import pytest

from utility_scripts.contracts import KBError
from utility_scripts.ingest import markdown_text


def test_footnotes_and_remote_images_preserved():
    text = '''# Protein regulation
Allostery[^1] and mutations[^Y220C] are discussed here.

[^1]: *Allostery changes protein function at a distant site.*
[^Y220C]: A mutation in the p53 DNA-binding domain.
    Further explanation with an [external source](https://example.org/paper).

![Protein network](https://example.org/network.png)
[reference]: https://example.org/paper
'''
    assert markdown_text(text.encode()) == text


@pytest.mark.parametrize('link', [
    '[figure]: assets/network.png',
    '[figure]: <assets/network.png>',
    '[^1]: See ![figure](assets/network.png).',
    '[^1]: Explanation.\n    See [data](results.csv).',
    '[^1]: See <img src="assets/network.png">.',
])
def test_local_dependencies_still_rejected(link):
    with pytest.raises(KBError, match='local or unsupported links'):
        markdown_text(link.encode())
