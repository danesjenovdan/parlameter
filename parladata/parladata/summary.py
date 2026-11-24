import os
from functools import lru_cache

import pymupdf
import requests
from django.conf import settings
from langchain.chat_models import init_chat_model

from parladata.models import Law, Link, Summary

# https://python.langchain.com/docs/integrations/chat/google_generative_ai/
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gemini-3.8-flash")
SUMMARY_MODEL_PROVIDER = os.getenv("SUMMARY_MODEL_PROVIDER", "google_genai")

SUMMARY_PROMPT = """Si pravni pomočnik, ki pripravlja kratke povzetke predlogov zakonov za širšo javnost.
Na podlagi spodnjega besedila predloga zakona napiši jedrnat povzetek v slovenščini (5-20 stavkov), ki pojasni:
- kaj predlog zakona ureja in kateri problem naslavlja,
- katere so ključne spremembe oz. novosti,
- na koga predlog vpliva.

Dokumenti predloga zakona:
{text}"""


@lru_cache
def _get_chat_model():
    return init_chat_model(
        SUMMARY_MODEL,
        model_provider=SUMMARY_MODEL_PROVIDER,
        api_key=settings.GOOGLE_API_KEY,
    )


def is_valid_pdf_data(data: str) -> bool:
    """
    Check if the extracted PDF data is valid (i.e., contains any non-empty text) and contains at least one non-empty page with minimal 200 non space characters.
    """
    data = data.replace(" ", "")
    return len(data) >= 500


def read_document(link_model) -> str | None:
    """
    Download pdf of the document linked by the link_model and extract text per page.
    """
    response = requests.get(link_model.url, timeout=30)
    response.raise_for_status()
    with pymupdf.open(stream=response.content, filetype="pdf") as pdf:
        data = "\n".join(page.get_text().strip() for page in pdf)
    if not data:
        return None
    if not is_valid_pdf_data("\n".join(data)):
        return None
    return data


def make_summary(links_queryset) -> str | None:
    """
    Generate a summary of the bill (predlog zakona) linked by the link_model.
    """
    all_data = []
    for link_obj in links_queryset:
        data = read_document(link_obj)
        if not data:
            link_obj.is_parsable = False
            link_obj.save()
        else:
            all_data.append(data)
    if not all_data:
        raise ValueError("No valid PDF data found for the provided links.")
    chat_model = _get_chat_model()
    response = chat_model.invoke(
        SUMMARY_PROMPT.format(text="\n\nNew Document\n\n".join(all_data))
    )
    return response


def create_summary(links_queryset) -> Summary | None:
    """
    Create and save a Summary object for the bill (predlog zakona) linked by the link_model.
    """
    law = links_queryset.first().legislation if links_queryset.exists() else None
    try:
        response = make_summary(links_queryset)
    except ValueError:
        summary = Summary.objects.create(
            text="",
            ai_model=SUMMARY_MODEL_PROVIDER,
            ai_model_version=None,
            prompt=None,
            law=law,
            error=Summary.Error.NO_VALID_PDF_DATA,
        )
        summary.links.set(links_queryset)
        return summary

    model_name = response.response_metadata["model_name"]

    content = response.content
    if isinstance(content, list):
        content = content[0]
        if isinstance(content, dict):
            content = content.get("text", "")
        elif isinstance(content, str):
            content = content
        else:
            raise ValueError(
                f"Unexpected content format in summary response. {response.content}"
            )
    elif isinstance(content, str):
        content = content
    else:
        raise ValueError(
            f"Unexpected content format in summary response. {response.content}"
        )

    links_queryset.update(is_parsable=True)
    summary = Summary.objects.create(
        text=content,
        ai_model=SUMMARY_MODEL_PROVIDER,
        ai_model_version=model_name,
        prompt=SUMMARY_PROMPT,
        law=law,
    )
    summary.links.set(links_queryset)
    return summary


def seed_summaries(document_tag="proposal"):
    """
    Seed summaries for all parsable links that do not yet have a summary.
    """
    proposal_links = Link.objects.filter(
        legislation__isnull=False,
        tags__name__icontains=document_tag,
        summary__isnull=True,
    ).exclude(is_parsable=False)

    legislation = proposal_links.distinct("legislation").values_list(
        "legislation", flat=True
    )

    for law in legislation:
        links = Link.objects.filter(legislation=law, tags__name__icontains=document_tag)
        summary = create_summary(links)
        if summary:
            print(law)


def seed():
    seed_summaries(document_tag="proposal")
    seed_summaries(document_tag="enacted")
