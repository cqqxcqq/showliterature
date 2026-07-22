import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('data/works.json', 'r', encoding='utf-8'))
for w in d['works']:
    if not w.get('is_archived') and w.get('type') in ('诗歌', '古诗'):
        c = w.get('content', '')
        has_dd = '\n\n' in c or '\r\n\r\n' in c
        has_cr = '\r\n' in c
        title = w['title'][:20]
        print(f'{title:25s} double_break={has_dd} cr_only={has_cr and not has_dd} len={len(c)}')
