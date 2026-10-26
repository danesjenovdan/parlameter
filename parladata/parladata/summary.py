import os
from functools import lru_cache

import pymupdf
import requests
from django.conf import settings
from langchain.chat_models import init_chat_model

from parladata.models import Law, Link, Summary

# https://python.langchain.com/docs/integrations/chat/google_generative_ai/
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gemini-2.5-flash")
SUMMARY_MODEL_PROVIDER = os.getenv("SUMMARY_MODEL_PROVIDER", "google_genai")

SUMMARY_PROMPT = """Si pravni pomočnik, ki pripravlja kratke povzetke predlogov zakonov za širšo javnost.
Na podlagi spodnjega besedila predloga zakona napiši jedrnat povzetek v slovenščini (5-20 stavkov), ki pojasni:
- kaj predlog zakona ureja in kateri problem naslavlja,
- katere so ključne spremembe oz. novosti,
- na koga predlog vpliva.

Dokument predloga zakona:
{text}"""


@lru_cache
def _get_chat_model():
    return init_chat_model(
        SUMMARY_MODEL,
        model_provider=SUMMARY_MODEL_PROVIDER,
        api_key=settings.GOOGLE_API_KEY,
    )


def read_document(link_model) -> list[str] | None:
    """
    Download pdf of the document linked by the link_model and extract text per page.
    """
    response = requests.get(link_model.url, timeout=30)
    response.raise_for_status()
    with pymupdf.open(stream=response.content, filetype="pdf") as pdf:
        data = [page.get_text().strip() for page in pdf]
    if not any(data):
        return None
    return data


def make_summary(link_model) -> str | None:
    """
    Generate a summary of the bill (predlog zakona) linked by the link_model.
    """
    data = read_document(link_model)
    if not data:
        return None
    chat_model = _get_chat_model()
    response = chat_model.invoke(SUMMARY_PROMPT.format(text="\n".join(data)))
    return response.content


def create_summary(link_model) -> Summary | None:
    """
    Create and save a Summary object for the bill (predlog zakona) linked by the link_model.
    """
    content = make_summary(link_model)
    if not content:
        link_model.is_parsable = False
        link_model.save()
        return None
    else:
        link_model.is_parsable = True
        link_model.save()
        summary = Summary.objects.create(
            link=link_model,
            text=content,
            ai_model=SUMMARY_MODEL_PROVIDER,
            ai_model_version=SUMMARY_MODEL,
            prompt=SUMMARY_PROMPT,
        )
        return summary


def seed_summaries():
    """
    Seed summaries for all parsable links that do not yet have a summary.
    """
    links = Link.objects.filter(
        legislation__isnull=False,
        name__icontains="Predloga zakona",
        summary__isnull=True,
    ).exclude(is_parsable=False)

    for link in links:
        summary = create_summary(link)
        if summary:
            print(link.legislation.id)
