"""Reemplaza placeholders AFILIADO-PENDIENTE por URLs reales en los artículos del blog."""
import pathlib

BLOG_DIR = pathlib.Path(__file__).parent.parent / "src" / "content" / "blog"

REEMPLAZOS = {
    "https://AFILIADO-PENDIENTE/headshotpro": "https://www.headshotpro.com?via=inmoia",
    "https://AFILIADO-PENDIENTE/beehiiv": "https://www.beehiiv.com/?via=orlando-lopez",
}


def main():
    total_archivos = 0
    total_sustituciones = 0

    for md_file in sorted(BLOG_DIR.glob("*.md")):
        contenido = md_file.read_text(encoding="utf-8")
        nuevo_contenido = contenido
        sustituciones_archivo = 0

        for placeholder, url_real in REEMPLAZOS.items():
            count = nuevo_contenido.count(placeholder)
            if count:
                nuevo_contenido = nuevo_contenido.replace(placeholder, url_real)
                sustituciones_archivo += count

        if sustituciones_archivo:
            md_file.write_text(nuevo_contenido, encoding="utf-8")
            total_archivos += 1
            total_sustituciones += sustituciones_archivo
            print(f"{md_file.name}: {sustituciones_archivo} sustitución(es)")

    print(f"\nTotal: {total_sustituciones} sustituciones en {total_archivos} archivo(s)")


if __name__ == "__main__":
    main()
