#!/usr/bin/env python3
"""
Generador automático de artículos SEO para INMOIA.
Lee la cola de keywords, genera el artículo con la API de Anthropic,
y hace commit+push al repositorio.
"""
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import anthropic

ROOT = Path(__file__).parent.parent
QUEUE_FILE = ROOT / "scripts" / "content-queue.json"
BLOG_DIR = ROOT / "src" / "content" / "blog"
AFILIADOS_FILE = ROOT / "scripts" / "afiliados.json"

UMBRAL_QUEUE_BAJA = 4

PROMPT_MAESTRO = """Eres redactor SEO experto en el sector inmobiliario y en inteligencia artificial,
escribiendo para INMOIA, un sitio en español neutro (mercado Chile/LatAm).

Escribe un artículo COMPLETO en formato Markdown optimizado para posicionar en
Google para la keyword: "{KEYWORD}".

Requisitos obligatorios:
- Extensión: 1.200 a 1.800 palabras.
- Tono: profesional, práctico, directo. Cero relleno. Cero "en este artículo veremos".
- Estructura: un H1 con la keyword, 4-7 secciones con H2/H3, y una sección final
  de "Preguntas frecuentes" con 3-4 preguntas en H3 (formato pensado para featured snippets).
- Incluye consejos accionables y ejemplos concretos del día a día de un corredor
  de propiedades o una inmobiliaria.
- Cuando menciones una categoría de herramienta (redacción, fotos, video, email,
  tasación), recomienda de forma NATURAL las herramientas indicadas abajo, usando
  exactamente este marcador donde corresponda: [[AFILIADO:nombre]]. No inventes links.
- Herramientas a recomendar en este artículo: {LISTA_AFILIADOS}.
- No uses la primera persona del plural de forma genérica. Escribe para el lector ("tú").
- No incluyas frontmatter; solo el cuerpo en Markdown empezando por el H1.

Devuelve SOLO el Markdown del artículo, sin comentarios ni explicaciones."""


def load_queue():
    with open(QUEUE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def load_afiliados():
    with open(AFILIADOS_FILE, encoding="utf-8") as f:
        return json.load(f)


def keyword_to_slug(keyword: str) -> str:
    slug = keyword.lower()
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ü": "u", "ñ": "n",
    }
    for src, dst in replacements.items():
        slug = slug.replace(src, dst)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug[:80]


def extract_title(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_first_paragraph(markdown: str) -> str:
    lines = markdown.splitlines()
    in_content = False
    for line in lines:
        if line.startswith("#"):
            in_content = True
            continue
        if in_content and line.strip() and not line.startswith("#"):
            clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
            clean = re.sub(r"\*+([^*]+)\*+", r"\1", clean)
            return clean.strip()[:160]
    return ""


def resolve_afiliado_markers(markdown: str, afiliados_data: dict, afiliados_keys: list) -> str:
    """Replace [[AFILIADO:key]] markers with inline links."""
    def replacer(match):
        key = match.group(1).strip().lower()
        if key in afiliados_data:
            item = afiliados_data[key]
            return f"[{item['nombre']}]({item['url']})"
        return match.group(0)
    return re.sub(r"\[\[AFILIADO:([^\]]+)\]\]", replacer, markdown)


def generate_article(keyword: str, afiliados_keys: list) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY no encontrada en el entorno.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    lista_afiliados = ", ".join(afiliados_keys) if afiliados_keys else "ninguna"

    prompt = PROMPT_MAESTRO.replace("{KEYWORD}", keyword).replace("{LISTA_AFILIADOS}", lista_afiliados)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def build_frontmatter(title: str, description: str, keyword: str, afiliados_keys: list) -> str:
    tags = [keyword.split()[0].capitalize(), "IA inmobiliaria"]
    afiliados_yaml = json.dumps(afiliados_keys, ensure_ascii=False)
    return f"""---
title: "{title}"
description: "{description}"
pubDate: {date.today().isoformat()}
tags: {json.dumps(tags, ensure_ascii=False)}
keyword: "{keyword}"
draft: false
afiliados: {afiliados_yaml}
---

"""


def git_commit_push(keyword: str):
    try:
        subprocess.run(["git", "config", "user.email", "actions@github.com"], cwd=ROOT, check=True)
        subprocess.run(["git", "config", "user.name", "INMOIA Bot"], cwd=ROOT, check=True)
        subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"post: {keyword}"],
            cwd=ROOT, check=True
        )
        subprocess.run(["git", "push"], cwd=ROOT, check=True)
        print(f"Push exitoso: post: {keyword}")
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}", file=sys.stderr)
        sys.exit(1)


def propose_new_keywords(current_queue: list) -> list:
    """When queue drops below threshold, generate new keyword proposals via API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return []

    client = anthropic.Anthropic(api_key=api_key)
    existing = [item["keyword"] for item in current_queue]
    existing_str = "\n".join(f"- {k}" for k in existing)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Eres un experto en SEO inmobiliario para el mercado chileno y latinoamericano.

Genera 10 nuevas keywords de long tail sobre inteligencia artificial aplicada al sector inmobiliario,
en español, que NO estén en esta lista existente:

{existing_str}

Responde SOLO con un JSON array de strings, sin explicaciones.
Ejemplo: ["keyword 1", "keyword 2"]"""
        }]
    )

    try:
        text = message.content[0].text.strip()
        new_keywords = json.loads(text)
        new_items = []
        for kw in new_keywords[:10]:
            new_items.append({
                "keyword": kw,
                "cluster": "F",
                "afiliados": ["writesonic", "frase"],
                "estado": "pendiente"
            })
        return new_items
    except Exception:
        return []


def main():
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    queue = load_queue()
    afiliados_data = load_afiliados()

    pending = [item for item in queue if item["estado"] == "pendiente"]

    if not pending:
        print("Cola vacía. No hay keywords pendientes.")
        sys.exit(0)

    item = pending[0]
    keyword = item["keyword"]
    afiliados_keys = item.get("afiliados", [])

    print(f"Generando artículo para: {keyword}")
    markdown = generate_article(keyword, afiliados_keys)
    markdown = resolve_afiliado_markers(markdown, afiliados_data, afiliados_keys)

    title = extract_title(markdown) or keyword.capitalize()
    description = extract_first_paragraph(markdown) or f"Guía completa sobre {keyword}."

    body = "\n".join(
        line for line in markdown.splitlines()
        if not (line.startswith("# ") and extract_title(markdown) in line)
    ) if title else markdown

    frontmatter = build_frontmatter(title, description, keyword, afiliados_keys)
    full_content = frontmatter + markdown

    slug = keyword_to_slug(keyword)
    output_path = BLOG_DIR / f"{slug}.md"
    output_path.write_text(full_content, encoding="utf-8")
    print(f"Artículo guardado: {output_path}")

    for item_in_queue in queue:
        if item_in_queue["keyword"] == keyword:
            item_in_queue["estado"] = "publicada"
            break
    save_queue(queue)

    remaining_pending = sum(1 for i in queue if i["estado"] == "pendiente") - 1
    if remaining_pending < UMBRAL_QUEUE_BAJA:
        print(f"Cola baja ({remaining_pending} pendientes). Proponiendo nuevas keywords...")
        new_items = propose_new_keywords(queue)
        if new_items:
            queue.extend(new_items)
            save_queue(queue)
            print(f"Se añadieron {len(new_items)} keywords nuevas a la cola.")

    git_commit_push(keyword)


if __name__ == "__main__":
    main()
