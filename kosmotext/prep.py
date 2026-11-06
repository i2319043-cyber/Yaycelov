#!/usr/bin/env python3
"""Запускается при сборке (у GitHub есть интернет): скачивает Three.js и шрифты Google
в assets и переписывает index.html на локальные файлы, чтобы приложение работало без сети."""
import os, re, sys, urllib.request

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src/main/assets')
UA = 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36'

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

p = os.path.join(A, 'index.html')
html = open(p, encoding='utf-8').read()

# Three.js — обязателен
three = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'
open(os.path.join(A, 'three.min.js'), 'wb').write(get(three))
assert three in html
html = html.replace(three, 'three.min.js')

# Шрифты — желательны (при ошибке остаётся ссылка в сеть)
try:
    m = re.search(r'<link href="(https://fonts\.googleapis\.com/css2[^"]+)" rel="stylesheet">', html)
    css = get(m.group(1).replace('&amp;', '&')).decode('utf-8')
    os.makedirs(os.path.join(A, 'fonts'), exist_ok=True)
    urls = sorted(set(re.findall(r'url\((https://[^)]+)\)', css)))
    for i, u in enumerate(urls):
        name = 'f%d.woff2' % i
        open(os.path.join(A, 'fonts', name), 'wb').write(get(u))
        css = css.replace(u, 'fonts/' + name)
    open(os.path.join(A, 'fonts.css'), 'w', encoding='utf-8').write(css)
    html = html.replace(m.group(0), '<link href="fonts.css" rel="stylesheet">')
    print('fonts:', len(urls))
except Exception as e:
    print('WARNING: fonts not bundled:', e, file=sys.stderr)

open(p, 'w', encoding='utf-8').write(html)
print('ok')
