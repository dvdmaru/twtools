#!/usr/bin/env python3
"""twtools 外部連結死鏈檢查（借 public-apis scripts/validate/links.py 的形狀，含 Cloudflare 誤判白名單）。

用法：python3 link-check.py <site-root> [--out report.md] [--json report.json]
- 只掃 <a href="http(s)://…"> 的絕對連結；自家 twtools.cc 與資產類主機不查。
- GET（非 HEAD）、瀏覽器 UA、逾時 20 秒、逾時再試一次、併發 8。
- 判死：狀態碼 >= 400、連線失敗、逾時兩次。
- Cloudflare 白名單：403／503 且 Server 含 cloudflare 且內文命中挑戰頁字串 → 記「擋 bot」不算死。
- 結束碼：0 無死鏈；1 有死鏈；2 掃描失敗。
"""
import argparse, concurrent.futures, html, json, os, re, sys, time, urllib.error, urllib.request

SKIP_HOSTS = {
    'twtools.cc', 'www.twtools.cc',
    'notebook.google.com',          # 需登入，永遠 302 到登入頁
    'fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.tailwindcss.com',
    'pagead2.googlesyndication.com', 'cdn.adotone.com',
    'line.me',                      # /R/share 分享跳轉
    'x.com', 'twitter.com', 'www.facebook.com', 'www.instagram.com', 'www.threads.net',  # 一律擋非登入 UA
}
CF_MARKERS = ('Just a moment', 'cf-chl', 'challenge-platform', 'Attention Required', 'cf-browser-verification')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36 twtools-link-check'
HREF_RE = re.compile(r'<a\s[^>]*?href="(https?://[^"#]+)', re.I)


def collect(root):
    links = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git', 'node_modules', 'blog-images', '_assets')]
        for f in fn:
            if not f.endswith('.html'):
                continue
            p = os.path.join(dp, f)
            try:
                txt = open(p, encoding='utf-8', errors='ignore').read()
            except OSError:
                continue
            rel = os.path.relpath(p, root)
            for m in HREF_RE.finditer(txt):
                u = html.unescape(m.group(1)).strip()
                host = re.sub(r'^https?://', '', u).split('/')[0].lower()
                if host in SKIP_HOSTS:
                    continue
                links.setdefault(u, set()).add(rel)
    return links


def probe(url, timeout=20):
    """用 curl 而不是 urllib：Python 3.13 對台灣政府網站的憑證鏈會丟 Missing Subject Key Identifier，
    整批 gov.tw 全部假死（2026-09-08 本機實測 57 條），curl 對同一批站回 200。"""
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as td:
        body_p, hdr_p = os.path.join(td, 'b'), os.path.join(td, 'h')
        cmd = ['curl', '-sS', '-L', '-m', str(timeout), '-A', UA,
               '-H', 'Accept: text/html,*/*;q=0.8', '-H', 'Accept-Language: zh-TW,zh;q=0.9,en;q=0.8',
               '-o', body_p, '-D', hdr_p, '-w', '%{http_code}', '--max-filesize', '2000000', url]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        except subprocess.TimeoutExpired:
            return 0, '', 'timeout'
        code = int(r.stdout.strip() or 0) if r.stdout.strip().isdigit() else 0
        if code == 0:
            return 0, '', (r.stderr.strip().split('\n')[-1][:80] if r.stderr else 'curl error')
        server, body = '', ''
        try:
            hdrs = open(hdr_p, encoding='utf-8', errors='ignore').read()
            m = re.findall(r'(?im)^server:\s*(.+)$', hdrs)
            server = m[-1].strip() if m else ''
            body = open(body_p, encoding='utf-8', errors='ignore').read(4096)
        except OSError:
            pass
        return code, server, body


def classify(url):
    code, server, body = probe(url)
    if code == 0:
        time.sleep(2)
        code, server, body = probe(url, timeout=30)
    if code == 0:
        return 'dead', code, body
    if code >= 400:
        if code in (403, 503) and 'cloudflare' in server.lower() and any(k in body for k in CF_MARKERS):
            return 'blocked', code, 'cloudflare challenge'
        if code in (403, 429):
            return 'blocked', code, 'bot 擋（無法判定死活）'
        return 'dead', code, ''
    return 'ok', code, ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--out', default=None)
    ap.add_argument('--json', default=None)
    ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args()
    links = collect(a.root)
    if not links:
        print('no links found', file=sys.stderr)
        return 2
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for url, res in zip(links, ex.map(classify, links)):
            results[url] = res
    dead = sorted(u for u, r in results.items() if r[0] == 'dead')
    blocked = sorted(u for u, r in results.items() if r[0] == 'blocked')
    ok = sum(1 for r in results.values() if r[0] == 'ok')
    lines = [f'# 外部連結死鏈檢查 {time.strftime("%Y-%m-%d %H:%M")}', '',
             f'- 掃描連結 {len(links)}：正常 {ok}、死鏈 {len(dead)}、擋 bot（不判死）{len(blocked)}', '']
    if dead:
        lines += ['## 死鏈', '', '| 連結 | 狀態 | 出現頁面 |', '|---|---|---|']
        for u in dead:
            code, note = results[u][1], results[u][2]
            lines.append(f'| {u} | {code or note} | {", ".join(sorted(links[u])[:3])} |')
        lines.append('')
    if blocked:
        lines += ['## 擋 bot（人工抽查，不算死）', '', '| 連結 | 狀態 | 備註 |', '|---|---|---|']
        for u in blocked:
            lines.append(f'| {u} | {results[u][1]} | {results[u][2]} |')
        lines.append('')
    report = '\n'.join(lines)
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(report)
    if a.json:
        json.dump({u: {'status': r[0], 'code': r[1], 'note': r[2], 'pages': sorted(links[u])} for u, r in results.items()},
                  open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(report)
    return 1 if dead else 0


if __name__ == '__main__':
    sys.exit(main())
