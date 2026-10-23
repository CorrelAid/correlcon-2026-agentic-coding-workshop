import pytest

from project.llm import provider_name


def test_eu_provider_allowed():
    assert provider_name("https://openai.inference.de-txl.ionos.com/v1") == "IONOS (DE)"


@pytest.mark.parametrize(
    "url", ["https://api.openai.com/v1", "https://api.anthropic.com", "http://localhost:11434/v1"]
)
def test_unapproved_providers_blocked(url):
    with pytest.raises(ValueError):
        provider_name(url)
