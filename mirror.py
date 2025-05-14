#!/usr/bin/env python3

import re
import click
import logging
import requests
import os
import hashlib
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

CSS_URL_BASE = "https://fonts.googleapis.com/css2"
FONT_BASE_URL = "https://fonts.gstatic.com"

def download_css(font_query: str, output_css: Path) -> str:
    params = {"family": font_query, "display": "swap"}
    r = requests.get(CSS_URL_BASE, params=params, headers={"User-Agent": UA})
    r.raise_for_status()
    output_css.write_text(r.text)
    return r.text

def extract_font_urls(css_text: str):
    return re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', css_text)

def download_fonts(urls, fonts_dir):
    fonts_dir = Path(fonts_dir)
    fonts_dir.mkdir(parents=True, exist_ok=True)
    url_map = {}

    for url in urls:
        # Get file extension
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix or ".font"
        # Hash the URL for a unique, short filename
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        filename = f"{url_hash}{ext}"
        local_path = fonts_dir / filename

        if not local_path.exists():
            r = requests.get(url, stream=True)
            r.raise_for_status()
            file_path = str(local_path)
            if os.name == "nt" and len(file_path) > 250:
                # Use absolute path and only backslashes for Windows long paths
                abs_path = os.path.abspath(local_path)
                abs_path = abs_path.replace("/", "\\")
                # Ensure the path is a valid Windows long path
                # Remove any trailing backslash
                if abs_path.endswith("\\"):
                    abs_path = abs_path.rstrip("\\")
                file_path = f"\\\\?\\{abs_path}"
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        url_map[url] = str(local_path)
    return url_map

def rewrite_css(css_text: str, url_map: dict, fonts_root: Path) -> str:
    new_css = css_text
    for url, path in url_map.items():
        relative_path = Path(path).relative_to(fonts_root.parent)
        new_css = new_css.replace(url, f"/{relative_path.as_posix()}")
    return new_css

def rewrite_css(css_content: str, output_dir: str) -> str:
    # Replace all src: url(/fonts/...) with the correct prefix
    return re.sub(
        r'src:\s*url\(/fonts/',
        f'src: url(/{output_dir}/fonts/',
        css_content
    )

@click.command()
@click.option('--fonts', '-f', multiple=True, required=False, help="Google Fonts query (e.g., 'Roboto:wght@100;400;700')")
@click.option('--fonts-file', type=click.Path(exists=True, dir_okay=False), help="Path to file containing font queries (one per line)")
@click.option('--output-dir', '-o', default="google_fonts_proxy", help="Output base directory")
def main(fonts, fonts_file, output_dir):
    font_list = list(fonts)
    if fonts_file:
        with open(fonts_file, "r", encoding="utf-8") as f:
            file_fonts = [
                line.strip().replace("+", " ")
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
            font_list.extend(file_fonts)
    if not font_list:
        raise click.UsageError("No fonts specified. Use --fonts/-f or --fonts-file.")

    base = Path(output_dir)
    css_dir = base / "css"
    fonts_dir = base / "fonts"
    css_dir.mkdir(parents=True, exist_ok=True)
    fonts_dir.mkdir(parents=True, exist_ok=True)

    for font in font_list:
        safe_name = font.replace(':', '_').replace('@', '_').replace(';', '_').replace('&', '_')
        css_path = css_dir / f"{safe_name}.css"
        logging.info(f"Fetching CSS for {font}")
        css_text = download_css(font, css_path)

        logging.info(f"Extracting font URLs from {css_path}")
        urls = extract_font_urls(css_text)

        logging.info(f"Downloading {len(urls)} fonts")
        url_map = download_fonts(urls, fonts_dir)

        logging.info("Rewriting CSS")
        updated_css = rewrite_css(css_text, url_map, fonts_dir)

        css_path.write_text(updated_css)
        logging.info(f"Saved rewritten CSS to {css_path}")

if __name__ == '__main__':
    main()
