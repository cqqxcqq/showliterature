#!/usr/bin/env python3
"""
Build script for static reader website.
Reads data/works.json, generates static HTML files to reader/dist/
"""

import json
import re
import shutil
from pathlib import Path

# ─── Paths ───
ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "works.json"
DIST_DIR = ROOT / "reader" / "dist"
READ_DIR = DIST_DIR / "read"

# ─── Google Fonts ───
GOOGLE_FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Noto+Serif+SC:wght@300;400;500;600"
    "&family=Noto+Sans+SC:wght@300;400;500"
    "&display=swap"
)

# ─── Shared CSS ───
SHARED_CSS = f"""@import url('{GOOGLE_FONTS}');

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%;}}

:root,[data-theme="light"]{{
  --bg:#f5f0e8;--text:#2b2520;--text-soft:#6b5e52;
  --meta:#a09283;--accent:#9a6d4a;--accent-hover:#7a5235;
  --toolbar-bg:rgba(245,240,232,.92);--toolbar-border:rgba(0,0,0,.06);
  --btn-active-bg:#9a6d4a;--btn-active-text:#fff;
}}
[data-theme="sepia"]{{
  --bg:#e4d5b8;--text:#3a2c18;--text-soft:#6b5a42;
  --meta:#8a7558;--accent:#8a3a1a;--accent-hover:#6a2a10;
  --toolbar-bg:rgba(228,213,184,.92);--toolbar-border:rgba(0,0,0,.08);
  --btn-active-bg:#8a3a1a;--btn-active-text:#fff;
}}
[data-theme="dark"]{{
  --bg:#14110d;--text:#d8ceb8;--text-soft:#9a8e7a;
  --meta:#6b6050;--accent:#c9a06c;--accent-hover:#ddb87e;
  --toolbar-bg:rgba(20,17,13,.92);--toolbar-border:rgba(255,255,255,.06);
  --btn-active-bg:#c9a06c;--btn-active-text:#14110d;
}}

[data-font="serif"] body{{font-family:'Noto Serif SC','Songti SC','STSong','SimSun',serif;}}
[data-font="kai"] body{{font-family:'Kaiti SC','STKaiti','KaiTi','SimKai',serif;}}
[data-font="fangsong"] body{{font-family:'FangSong','STFangsong','FangSong_GB2312',serif;}}
[data-font="sans"] body{{font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif;}}

[data-size="sm"] body{{font-size:1rem;line-height:2;letter-spacing:.02em;}}
[data-size="md"] body{{font-size:1.125rem;line-height:2.15;letter-spacing:.02em;}}
[data-size="lg"] body{{font-size:1.3rem;line-height:2.3;letter-spacing:.02em;}}

body{{
  background:var(--bg);color:var(--text);
  transition:background .35s ease,color .35s ease;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
  min-height:100vh;
}}
"""

# ─── Library CSS ───
LIBRARY_CSS = SHARED_CSS + """
.back-link{
  position:fixed;top:0;left:0;z-index:10;
  padding:1.25rem 1.5rem;
  font-size:.9rem;color:var(--meta);text-decoration:none;
  transition:color .2s ease;
}
.back-link:hover{color:var(--accent);}
.library{padding:5rem 1.5rem 4rem;max-width:720px;margin:0 auto;}
.library-header{text-align:center;margin-bottom:3rem;}
.library-header h1{font-size:1.8rem;font-weight:600;color:var(--text);margin-bottom:.5rem;letter-spacing:.05em;}
.library-header p{color:var(--meta);font-size:.9rem;}
.work-list{display:flex;flex-direction:column;gap:.125rem;}
.work-item{
  display:block;padding:1.1rem 1.25rem;
  text-decoration:none;color:inherit;
  border-radius:8px;transition:background .2s ease;
}
.work-item:hover{background:rgba(0,0,0,.03);}
[data-theme="dark"] .work-item:hover{background:rgba(255,255,255,.04);}
.work-item .wi-title{font-size:1.05rem;font-weight:500;color:var(--text);margin-bottom:.35rem;line-height:1.5;}
.work-item .wi-meta{font-size:.8rem;color:var(--meta);display:flex;gap:.75rem;flex-wrap:wrap;}
.work-item .wi-excerpt{font-size:.85rem;color:var(--text-soft);margin-top:.4rem;line-height:1.7;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
@media (max-width:640px){
  .library{padding:4rem 1rem 3rem;}
  .back-link{padding:1rem 1.25rem;}
}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{transition-duration:.01ms!important;}
}
"""

# ─── Reader CSS ───
READER_CSS = SHARED_CSS + """
.back-link{
  position:fixed;top:0;left:0;z-index:10;
  padding:1.25rem 1.5rem;
  font-size:.9rem;color:var(--meta);text-decoration:none;
  transition:color .2s ease;
}
.back-link:hover{color:var(--accent);}
.reader{padding:5rem 1.5rem 7rem;max-width:820px;margin:0 auto;}
.reader-header{text-align:center;margin-bottom:3rem;}
.reader-header h1{font-size:1.75rem;font-weight:600;color:var(--text);margin-bottom:.6rem;line-height:1.5;letter-spacing:.04em;}
.reader-header .meta{font-size:.85rem;color:var(--meta);display:flex;justify-content:center;gap:.5rem;flex-wrap:wrap;}
.reader-header .meta span{display:inline-flex;align-items:center;}
.reader-header .meta .dot{margin:0 .15rem;opacity:.4;}
.reader-body p{
  margin-bottom:2em;text-indent:2em;line-height:inherit;color:var(--text);
}
.reader-body p:last-child{margin-bottom:0;}

.toolbar{
  position:fixed;bottom:0;left:0;right:0;z-index:100;
  display:flex;align-items:center;justify-content:center;
  gap:0;padding:.65rem 1rem;
  background:var(--toolbar-bg);
  border-top:1px solid var(--toolbar-border);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  transition:background .35s ease,border-color .35s ease,transform .3s ease,opacity .3s ease;
}
.toolbar.hidden{transform:translateY(100%);opacity:0;pointer-events:none;}
.toolbar-group{display:flex;align-items:center;gap:0;}
.toolbar-divider{width:1px;height:18px;background:var(--toolbar-border);margin:0 .6rem;flex-shrink:0;}
.toolbar-btn{
  display:inline-flex;align-items:center;justify-content:center;
  min-width:36px;height:36px;padding:0 .5rem;
  border:none;border-radius:6px;background:transparent;
  color:var(--text-soft);font-size:.85rem;font-weight:400;cursor:pointer;
  font-family:inherit;white-space:nowrap;
  transition:background .15s ease,color .15s ease;
}
.toolbar-btn:hover{background:rgba(0,0,0,.05);}
[data-theme="dark"] .toolbar-btn:hover{background:rgba(255,255,255,.08);}
.toolbar-btn:active{transform:scale(.95);}
.toolbar-btn.active{
  background:var(--btn-active-bg);color:var(--btn-active-text);font-weight:500;
}
.toolbar-btn.size-btn{font-size:.8rem;font-weight:500;padding:0 .45rem;min-width:32px;}

@media (max-width:640px){
  .reader{padding:4rem 1.25rem 6.5rem;}
  .back-link{padding:1rem 1.25rem;}
  .toolbar{padding:.55rem .75rem;}
  .toolbar-btn{min-width:32px;height:32px;font-size:.8rem;padding:0 .4rem;}
  .toolbar-divider{margin:0 .4rem;}
}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{transition-duration:.01ms!important;}
}
"""

# ─── Library HTML Template ───
LIBRARY_HTML = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="{theme}" data-font="{font}" data-size="{size}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="{fonts_url}">
<link rel="stylesheet" href="{fonts_url}" media="print" onload="this.media='all'">
<style>{css}</style>
</head>
<body>
<a href="admin.html" class="back-link" style="left:auto;right:0;opacity:.4;font-size:.8rem;">管理</a>
<main class="library">
  <header class="library-header">
    <h1>{title}</h1>
    <p id="lib-stats">加载中...</p>
  </header>
  <div id="work-list"></div>
</main>
<script>{lib_js}</script>
</body>
</html>"""

# ─── Reader HTML Template ───
READER_HTML = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="{theme}" data-font="{font}" data-size="{size}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="{fonts_url}">
<link rel="stylesheet" href="{fonts_url}" media="print" onload="this.media='all'">
<style>{css}</style>
</head>
<body>
<a href="../index.html" class="back-link">← 返回</a>
<main class="reader">
  <header class="reader-header">
    <h1>{title}</h1>
    <div class="meta">
      <span>{type}</span><span class="dot">·</span>
      <span>{char_count} 字</span><span class="dot">·</span>
      <span>{writing_date}</span>
    </div>
  </header>
  <div class="reader-body">{paragraphs}</div>
</main>
<div class="toolbar" id="toolbar">
  <div class="toolbar-group">
    <button class="toolbar-btn theme-btn" id="btn-theme">亮</button>
  </div>
  <div class="toolbar-divider"></div>
  <div class="toolbar-group">
    <button class="toolbar-btn size-btn" id="btn-size-minus">A-</button>
    <button class="toolbar-btn size-btn" id="btn-size-plus">A+</button>
  </div>
  <div class="toolbar-divider"></div>
  <div class="toolbar-group">
    <button class="toolbar-btn font-btn" id="btn-font">宋</button>
  </div>
</div>
<script>{reader_js}</script>
</body>
</html>"""

# ─── Library JS ───
LIB_JS = """(function(){
  var h=document.documentElement,K='reader_prefs';
  function l(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return{}}}
  function a(p){if(p.theme)h.dataset.theme=p.theme;if(p.font)h.dataset.font=p.font;if(p.size)h.dataset.size=p.size;}
  a(l());
  window.addEventListener('storage',function(e){if(e.key===K)a(JSON.parse(e.newValue||'{}'));});

  fetch('works.json').then(function(r){return r.json();}).then(function(data){
    var works=(data.works||[]).filter(function(w){return !w.is_archived;});
    works.sort(function(a,b){return (b.added_date||'').localeCompare(a.added_date||'');});
    var totalChars=works.reduce(function(s,w){return s+(w.char_count||0);},0);
    document.getElementById('lib-stats').textContent=works.length+' 篇作品 · 共 '+totalChars+' 字';
    var list=document.getElementById('work-list');
    if(works.length===0){list.innerHTML='<div style="text-align:center;padding:4rem 1rem;color:var(--text2);">暂无作品</div>';return;}
    list.innerHTML='<div class="work-list">'+works.map(function(w){
      var paras=(w.content||'').split(/\\r?\\n\\r?\\n/);
      var excerpt=paras[0]?paras[0].substring(0,100)+'…':'';
      return '<a href="read/'+w.id+'.html" class="work-item">'+
        '<div class="wi-title">'+esc(w.title||'无标题')+'</div>'+
        '<div class="wi-meta">'+
          '<span>'+esc(w.type||'')+'</span>'+
          '<span>'+(w.char_count||0)+' 字</span>'+
          '<span>'+esc(w.writing_date||'')+'</span>'+
        '</div>'+
        '<div class="wi-excerpt">'+esc(excerpt)+'</div>'+
      '</a>';
    }).join('')+'</div>';
  }).catch(function(e){
    document.getElementById('work-list').innerHTML='<div style="text-align:center;padding:4rem 1rem;color:var(--text2);">加载作品失败</div>';
  });

  function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
})();"""

# ─── Reader JS ───
READER_JS = """(function(){
  var h=document.documentElement;
  var toolbar=document.getElementById('toolbar');
  var btnTheme=document.getElementById('btn-theme');
  var btnFont=document.getElementById('btn-font');
  var btnSizeMinus=document.getElementById('btn-size-minus');
  var btnSizePlus=document.getElementById('btn-size-plus');
  var K='reader_prefs';
  var THEMES=['light','sepia','dark'];
  var THEME_LABELS={'light':'亮','sepia':'护','dark':'暗'};
  var FONTS=['serif','kai','fangsong','sans'];
  var FONT_LABELS={'serif':'宋','kai':'楷','fangsong':'仿','sans':'黑'};
  var SIZES=['sm','md','lg'];
  var p=l(),lastY=0,timer=null;

  function l(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return{}}}
  function s(v){localStorage.setItem(K,JSON.stringify(v));}
  function apply(v){
    if(v.theme){h.dataset.theme=v.theme;btnTheme.textContent=THEME_LABELS[v.theme]||'亮';}
    if(v.font){h.dataset.font=v.font;btnFont.textContent=FONT_LABELS[v.font]||'宋';}
    if(v.size){h.dataset.size=v.size;}
  }
  function cycle(arr,cur){var i=arr.indexOf(cur);return arr[(i+1)%arr.length];}
  apply(p);

  btnTheme.addEventListener('click',function(){
    p.theme=cycle(THEMES,p.theme||'light');
    apply(p);s(p);
  });
  btnFont.addEventListener('click',function(){
    p.font=cycle(FONTS,p.font||'serif');
    apply(p);s(p);
  });
  btnSizeMinus.addEventListener('click',function(){
    var i=SIZES.indexOf(p.size||'md');
    p.size=SIZES[Math.max(0,i-1)];
    apply(p);s(p);
  });
  btnSizePlus.addEventListener('click',function(){
    var i=SIZES.indexOf(p.size||'md');
    p.size=SIZES[Math.min(SIZES.length-1,i+1)];
    apply(p);s(p);
  });

  document.addEventListener('keydown',function(e){
    if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA')return;
    if(e.key==='t'||e.key==='T')btnTheme.click();
    else if(e.key==='f'||e.key==='F')btnFont.click();
    else if(e.key==='-'||e.key==='_')btnSizeMinus.click();
    else if(e.key==='='||e.key==='+')btnSizePlus.click();
    else if(e.key==='ArrowLeft')history.back();
  });

  function onScroll(){
    var y=window.scrollY;
    if(y>lastY&&y>100){toolbar.classList.add('hidden');}
    else{toolbar.classList.remove('hidden');}
    lastY=y;
    clearTimeout(timer);
    timer=setTimeout(function(){if(window.scrollY>100)toolbar.classList.add('hidden');},2500);
  }
  window.addEventListener('scroll',onScroll,{passive:true});

  window.addEventListener('storage',function(e){
    if(e.key===K){p=JSON.parse(e.newValue||'{}');apply(p);}
  });
})();"""

def load_works():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    works = [w for w in data.get('works', []) if not w.get('is_archived', False)]
    works.sort(key=lambda w: w.get('added_date', '0000-00-00 00:00'), reverse=True)
    return works

def split_paragraphs(content):
    paras = re.split(r'\r?\n\r?\n', content.strip())
    return [p.strip() for p in paras if p.strip()]

def build_library():
    html = LIBRARY_HTML.format(
        theme='dark', font='serif', size='md',
        title='书架',
        css=LIBRARY_CSS,
        fonts_url=GOOGLE_FONTS,
        lib_js=LIB_JS
    )
    (DIST_DIR / 'index.html').write_text(html, encoding='utf-8')
    print(f"Generated index.html (dynamic, loads works.json at runtime)")

def build_reader(work):
    paragraphs = ''.join(f'<p>{p}</p>' for p in split_paragraphs(work['content']))
    html = READER_HTML.format(
        theme='dark', font='serif', size='md',
        title=work['title'],
        type=work.get('type', ''),
        char_count=work.get('char_count', 0),
        writing_date=work.get('writing_date', ''),
        paragraphs=paragraphs,
        css=READER_CSS,
        fonts_url=GOOGLE_FONTS,
        reader_js=READER_JS
    )
    (READ_DIR / f"{work['id']}.html").write_text(html, encoding='utf-8')
    print(f"Generated read/{work['id']}.html")

def main():
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    READ_DIR.mkdir(parents=True)

    works = load_works()
    print(f"Loaded {len(works)} works (archived excluded)")

    build_library()
    for w in works:
        build_reader(w)

    shutil.copy2(DATA_FILE, DIST_DIR / 'works.json')
    print(f"Copied works.json to dist/")

    # Copy admin page
    admin_src = ROOT / 'reader' / 'admin.html'
    if admin_src.exists():
        shutil.copy2(admin_src, DIST_DIR / 'admin.html')
        print("Copied admin.html to dist/")

    vercel_config = {'outputDirectory': 'reader/dist'}
    (ROOT / 'vercel.json').write_text(json.dumps(vercel_config, indent=2), encoding='utf-8')
    print("Created vercel.json")

    print(f"\nBuild complete! Output: {DIST_DIR}")

if __name__ == '__main__':
    main()
