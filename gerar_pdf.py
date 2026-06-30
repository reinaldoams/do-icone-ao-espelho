#!/usr/bin/env python3
"""Gera PDF em slides paisagem com imagens embutidas."""
import base64
import mimetypes
import os
import re
import subprocess
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
HTML_SLIDES = os.path.join(BASE, "catalogo_slides.html")
HTML_EMB = os.path.join(BASE, "catalogo_slides_embed.html")
PDF_OUT = os.path.join(BASE, "catalogo_exposicao.pdf")
IMGDIR = os.path.join(BASE, "imagens")
CACHE = os.path.join(BASE, "imagens_resized")

ALIASES = {"venus.jpg": "nascimento_venus.jpg", "atenas.jpg": "escola_atenas.jpg"}


def is_valid_image(path):
    if not os.path.isfile(path) or os.path.getsize(path) < 8000:
        return False
    with open(path, "rb") as f:
        head = f.read(4)
    return head[:3] == b"\xff\xd8\xff" or head == b"\x89PNG"


def resolve_image(name):
    path = os.path.join(IMGDIR, name)
    if is_valid_image(path):
        return path
    alt_name = ALIASES.get(name)
    if alt_name:
        alt = os.path.join(IMGDIR, alt_name)
        if is_valid_image(alt):
            return alt
    raise FileNotFoundError(f"Imagem não encontrada: {name}")


def resize_for_slide(path, name):
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, name)
    if os.path.isfile(out) and os.path.getmtime(out) >= os.path.getmtime(path):
        return out
    subprocess.run(
        ["convert", path, "-resize", "700x520>", "-quality", "82", out],
        check=True, capture_output=True,
    )
    return out


def to_data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode('ascii')}"


def main():
    with open(HTML_SLIDES, encoding="utf-8") as f:
        html = f.read()

    used = set(re.findall(r"IMG:(\w+\.jpg)", html))
    print(f"Embutindo {len(used)} imagens...")
    for name in sorted(used):
        path = resolve_image(name)
        small = resize_for_slide(path, name)
        uri = to_data_uri(small)
        html = html.replace(f"IMG:{name}", uri)
        print(f"  {name}: {os.path.getsize(small)//1024} KB")

    # quebra explícita antes de cada slide (exceto capa)
    html = re.sub(
        r'<div class="slide (?!capa)',
        r'<p style="page-break-before:always;margin:0;padding:0;height:0;font-size:1pt;line-height:0;">&nbsp;</p><div class="slide ',
        html,
    )

    with open(HTML_EMB, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML: {os.path.getsize(HTML_EMB)//1024//1024} MB")

    print("Gerando PDF paisagem...")
    r = subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", HTML_EMB, "--outdir", BASE],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stderr or r.stdout)
        raise SystemExit(r.returncode)

    emb_pdf = os.path.join(BASE, "catalogo_slides_embed.pdf")
    if os.path.isfile(emb_pdf):
        os.replace(emb_pdf, PDF_OUT)

    dl = os.path.expanduser("~/Downloads/catalogo_exposicao.pdf")
    with open(PDF_OUT, "rb") as s, open(dl, "wb") as d:
        d.write(s.read())

    pages = len(re.findall(rb"/Type\s*/Page[^s]", open(PDF_OUT, "rb").read()))
    print(f"PDF: {PDF_OUT}")
    print(f"Cópia: {dl}")
    print(f"{os.path.getsize(PDF_OUT)//1024} KB | {pages} slides")


if __name__ == "__main__":
    main()
