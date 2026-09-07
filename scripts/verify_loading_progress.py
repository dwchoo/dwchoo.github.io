#!/usr/bin/env python3
"""Verify byte-based download progress with throttled and gzip HTTP responses."""
from functools import partial
import gzip
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/verification'
PLY = (ROOT / 'assets/data/vggt/reconstruction.ply').read_bytes()
GZIP = gzip.compress(PLY)


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.startswith('/preview/'):
            self.path = self.path[len('/preview'):]
        if self.path != '/assets/data/vggt/reconstruction.ply':
            return super().do_GET()
        mode = self.server.mode
        gate = self.server.gate
        payload = GZIP if mode == 'gzip' else PLY
        if mode == 'truncated':
            payload = payload[:-1024]
        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        if mode == 'gzip':
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(payload)))
        # Other modes intentionally omit Content-Length; the manifest has decoded size.
        self.end_headers()
        try:
            middle = (len(payload) + 1) // 2
            self.wfile.write(payload[:middle])
            self.wfile.flush()
            gate.wait(timeout=20)
            for offset in range(middle, len(payload), 65536):
                self.wfile.write(payload[offset:offset + 65536])
                self.wfile.flush()
                time.sleep(.005)
        except (BrokenPipeError, ConnectionResetError):
            pass


def run():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results, errors = [], []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--enable-unsafe-swiftshader'])
            for mode in ['plain', 'gzip', 'truncated', 'abort']:
                server.mode = mode
                server.gate = threading.Event()
                mobile = mode == 'gzip'
                context = browser.new_context(viewport={'width':390 if mobile else 1440, 'height':844 if mobile else 1100},
                                              is_mobile=mobile, has_touch=mobile)
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.add_init_script('''
                  window.__phases = [];
                  document.addEventListener('DOMContentLoaded', () => {
                    const host = document.querySelector('[data-pointcloud-viewer]');
                    new MutationObserver(() => {
                      window.__phases.push({state: host.dataset.viewerState,
                        value: host.querySelector('progress').getAttribute('value')});
                    }).observe(host, {attributes:true, attributeFilter:['data-viewer-state']});
                  });
                ''')
                page.goto(f'http://127.0.0.1:{server.server_port}/' + ('preview/' if mobile else ''), wait_until='domcontentloaded')
                page.locator('[data-pointcloud-viewer]').scroll_into_view_if_needed()
                page.wait_for_function("document.querySelector('progress').value > 0 && document.querySelector('progress').value < 100")
                page.wait_for_timeout(150)
                value = float(page.locator('progress').get_attribute('value'))
                assert page.locator('[data-pointcloud-viewer]').get_attribute('aria-busy') == 'true'
                assert f'/ {len(PLY)/1e6:.1f} MB' in page.locator('[data-viewer-progress-text]').inner_text()
                if mode == 'plain':
                    page.wait_for_function("document.querySelector('progress').value === 50", timeout=10000)
                    value = float(page.locator('progress').get_attribute('value'))
                if mode == 'abort':
                    page.evaluate("document.querySelector('[data-pointcloud-viewer]').remove()")
                    server.gate.set()
                    page.wait_for_timeout(300)
                    assert page.locator('canvas').count() == 0
                    results.append({'mode':mode,'result':'PASS'})
                    context.close()
                    continue
                page.locator('[data-lang-button="kr"]').click()
                assert '다운로드하는 중' in page.locator('[data-viewer-status]').inner_text()
                # Bytes may keep arriving during the language click; progress must not reset.
                assert value <= float(page.locator('progress').get_attribute('value')) < 100
                page.locator('#tab-hdf').click()
                assert not page.locator('[data-viewer-progress]').is_visible()
                page.locator('#tab-vggt').click()
                assert page.locator('[data-viewer-progress]').is_visible()
                page.locator('[data-pointcloud-viewer]').scroll_into_view_if_needed()
                if mode in ['plain','gzip']:
                    page.screenshot(path=str(OUT / f'loading-{mode}.png'))
                server.gate.set()
                expected = 'file' if mode == 'truncated' else 'ready'
                page.wait_for_function("state => document.querySelector('[data-pointcloud-viewer]').dataset.viewerState === state", arg=expected)
                assert not page.locator('[data-viewer-progress]').is_visible()
                assert page.locator('[data-pointcloud-viewer]').get_attribute('aria-busy') == 'false'
                phases = page.evaluate('window.__phases')
                if expected == 'ready':
                    assert any(x['state']=='preparing' and x['value']=='100' for x in phases), phases
                    assert '500,000점' in page.locator('[data-viewer-status]').inner_text()
                else:
                    assert '불러올 수 없습니다' in page.locator('[data-viewer-status]').inner_text()
                results.append({'mode':mode,'partial_percent':value,'decoded_bytes':len(PLY),
                                'transfer_bytes':len(GZIP) if mobile else len(PLY) - (1024 if mode == 'truncated' else 0),
                                'result':'PASS','phases':phases})
                context.close()
            browser.close()
    finally:
        server.shutdown()
    assert not errors, errors
    report = {'results':results,'unhandled_errors':errors}
    (OUT / 'loading-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__ == '__main__':
    run()
