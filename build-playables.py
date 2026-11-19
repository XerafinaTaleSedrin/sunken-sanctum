"""Package the YouTube Playables bundle and check it against the published limits.

Run from the repo root:  python build-playables.py
Writes dist/sunken-sanctum-playables.zip with index.html at the root.
Limits: https://developers.google.com/youtube/gaming/playables/certification/requirements_stability
"""
import os, re, sys, zipfile

FILES = ['index.html'] + sorted('fonts/' + f for f in os.listdir('fonts') if f.endswith(('.woff2', '.txt')))
OUT = 'dist/sunken-sanctum-playables.zip'
MiB = 1024 * 1024
problems = []

total = 0
for f in FILES:
    n = os.path.getsize(f)
    total += n
    if n >= 30 * MiB:
        problems.append(f'{f}: {n} bytes, over the 30 MiB file limit')
    if not re.fullmatch(r'[A-Za-z0-9_.\-/]+', f):
        problems.append(f'{f}: file name has characters outside A-Z a-z 0-9 _ - .')
if len(FILES) > 8000:
    problems.append(f'{len(FILES)} files, over the 8000 limit')
if total >= 30 * MiB:
    problems.append(f'{total} bytes, over the 30 MiB initial bundle limit')

html = open('index.html', encoding='utf-8').read()
urls = set(re.findall(r'(?:src|href)\s*=\s*["\']?(https?://[^"\'\s>]+)', html))
urls |= set(re.findall(r'url\((https?://[^)]+)\)', html))
outside = sorted(u for u in urls if u != 'https://www.youtube.com/game_api/v1')
if outside:
    problems.append('external references: ' + ', '.join(outside))
if 'https://www.youtube.com/game_api/v1' not in html:
    problems.append('the Playables SDK script is missing')
sdk, game = html.find('game_api/v1'), html.find('const DATA = ')
if game != -1 and sdk > game:
    problems.append('the SDK script must come before the game code')
for bad in ('<a href', 'navigator.language', 'visibilitychange', 'fonts.googleapis', 'claude:'):
    if bad in html:
        problems.append(f'found "{bad}"')

if problems:
    print('NOT PACKAGED:\n  ' + '\n  '.join(problems))
    sys.exit(1)

os.makedirs('dist', exist_ok=True)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in FILES:
        z.write(f, f)
print(f'{OUT}: {len(FILES)} files, {total} bytes before compression, {os.path.getsize(OUT)} bytes zipped')
for f in FILES:
    print(f'  {f}  {os.path.getsize(f)}')
