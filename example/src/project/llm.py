"""Single point of access to the language model.

All LLM calls in the project go through this module. The provider is configured only in
`.env` (OpenAI-compatible API). Switching providers – e.g. when the NGO takes over the
project with its own contract – needs no code change.
"""

from __future__ import annotations

import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)  # .env wins – even if the agent's shell blanks the key

# Hosts with contractually guaranteed processing in the EU (see SETUP.md).
# Only add new providers after checking location, DPA and training policy.
EU_HOSTS: dict[str, str] = {
    "openai.inference.de-txl.ionos.com": "IONOS (DE)",
    "api.openai-compat.model-serving.eu01.onstackit.cloud": "STACKIT (DE)",
    "api.scaleway.ai": "Scaleway (FR)",
    "oai.endpoints.kepler.ai.cloud.ovh.net": "OVHcloud (FR)",
    "api.mistral.ai": "Mistral (FR) – paid plan with training opt-out only",
}

CODING_MODEL = os.getenv("LLM_MODEL_CODING", "Qwen/Qwen3-Coder-Next")
ANALYSIS_MODEL = os.getenv("LLM_MODEL_ANALYSIS", "openai/gpt-oss-120b")


def provider_name(base_url: str) -> str:
    """Return the provider for a base URL, or raise if it is not an approved EU provider."""
    host = urlparse(base_url).hostname or ""
    if host not in EU_HOSTS:
        raise ValueError(
            f"Endpoint '{host}' is not an approved EU provider. Add it to EU_HOSTS in "
            "src/project/llm.py only after checking location, DPA and training policy."
        )
    return EU_HOSTS[host]


def get_client() -> OpenAI:
    """OpenAI-compatible client for the configured EU provider."""
    base_url = os.getenv("LLM_BASE_URL", "")
    api_key = os.getenv("LLM_API_KEY", "")
    if not base_url or not api_key:
        raise RuntimeError("Set LLM_BASE_URL and LLM_API_KEY in .env (template: .env.example).")
    provider_name(base_url)  # aborts if the endpoint is not approved
    return OpenAI(base_url=base_url, api_key=api_key)


def chat(prompt: str, system: str | None = None, model: str | None = None, **kwargs) -> str:
    """Simple chat call. Returns only the answer text."""
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    response = get_client().chat.completions.create(
        model=model or ANALYSIS_MODEL, messages=messages, temperature=0, **kwargs
    )
    return response.choices[0].message.content or ""
