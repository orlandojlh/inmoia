"""Reemplaza el placeholder AFILIADO-PENDIENTE de Frase por el link real en los artículos del blog."""
import pathlib

BLOG_DIR = pathlib.Path(__file__).parent.parent / "src" / "content" / "blog"

PLACEHOLDER = "https://AFILIADO-PENDIENTE/frase"
URL_REAL = "https://www.frase.io/?via=inmoia69"


def main():
    total_archivos = 0
    total_sustituciones = 0

    for md_file in sorted(BLOG_DIR.glob("*.md")):
        contenido = md_file.read_text(encoding="utf-8")
        count = contenido.count(PLACEHOLDER)

        if count:
            nuevo_contenido = contenido.replace(PLACEHOLDER, URL_REAL)
            md_file.write_text(nuevo_contenido, encoding="utf-8")
            total_archivos += 1
            total_sustituciones += count
            print(f"{md_file.name}: {count} sustitución(es)")

    print(f"\nTotal: {total_sustituciones} sustituciones en {total_archivos} archivo(s)")


if __name__ == "__main__":
    main()
