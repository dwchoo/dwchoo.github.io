#!/usr/bin/env python3
"""Run local Chromium QA; install playwright in a temporary venv first."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/verification"


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/preview/"):
            self.path = self.path[len("/preview"):]
        super().do_GET()

    def log_message(self, *args):
        pass


def instrument(route):
    # Only the test response gets inspection hooks. Shipped JS has no debug API.
    source = (ROOT / "assets/js/pointcloud-viewer.js").read_text()
    source = source.replace("if (canRender()) renderer.render(scene, camera);", """
      if (canRender()) {
        renderer.render(scene, camera);
        window.__draws = (window.__draws || 0) + 1;
        window.__firstDraw ??= performance.now();
      }
    """)
    source = source.replace("return { setActive, setLanguage, dispose };", """
      window.__qa = () => ({
        state, disposed, draws: window.__draws || 0,
        position: camera?.position.toArray(), target: controls?.target.toArray(),
        distance: controls?.getDistance(),
        direction: camera?.position.clone().sub(controls.target).normalize().toArray(),
        vertices: geometry?.attributes.position.count,
        color: Array.from(geometry?.attributes.color.array.slice(0, 3) || []),
        ratio: renderer?.getPixelRatio(),
        geometryCount: scene?.children.length,
        size: material?.size, attenuation: material?.sizeAttenuation,
        near: camera?.near, far: camera?.far,
        enabled: controls?.enabled,
      });
      window.__disposeViewer = dispose;
      return { setActive, setLanguage, dispose };
    """)
    route.fulfill(status=200, content_type="text/javascript", body=source)


def settle(page):
    page.wait_for_timeout(180)


def snapshot(page):
    settle(page)
    return page.evaluate("window.__qa()")


def assert_close(a, b, tolerance=1e-8):
    if isinstance(a, list):
        assert all(abs(x-y) < tolerance for x, y in zip(a, b)), (a, b)
    else:
        assert abs(a-b) < tolerance, (a, b)


def wait_ready(page):
    page.locator('[data-pointcloud-viewer]').scroll_into_view_if_needed()
    page.wait_for_function("document.querySelector('[data-pointcloud-viewer]').dataset.viewerState === 'ready'")
    page.wait_for_function("window.__draws > 0")
    settle(page)


def drag(page, button="left", dx=100, dy=35):
    box = page.locator('canvas').bounding_box()
    x, y = box['x'] + box['width'] * .5, box['y'] + box['height'] * .5
    page.mouse.move(x, y)
    page.mouse.down(button=button)
    page.mouse.move(x+dx, y+dy, steps=8)
    page.mouse.up(button=button)
    settle(page)


def touch(page, two=False):
    cdp = page.context.new_cdp_session(page)
    b = page.locator('canvas').bounding_box()
    x, y = b['x'] + b['width']*.4, b['y'] + b['height']*.45
    def points(step):
        result = [{'x': x-step, 'y': y+step*.2, 'id': 1}]
        if two: result.append({'x': x+80+step, 'y': y+30, 'id': 2})
        return result
    cdp.send('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':points(0)})
    for step in [5, 10, 20, 30]:
        cdp.send('Input.dispatchTouchEvent', {'type':'touchMove','touchPoints':points(step)})
    cdp.send('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]})
    cdp.detach()
    settle(page)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    results = []
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--enable-unsafe-swiftshader'])
        version = browser.version
        for path, mobile in [('/', False), ('/preview/', True)]:
            context = browser.new_context(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 1100},
                                          is_mobile=mobile, has_touch=mobile, device_scale_factor=3 if mobile else 1)
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.on('response', lambda r: errors.append(f"HTTP {r.status}: {r.url}") if r.status >= 400 else None)
            requests = []
            page.on('request', lambda r: requests.append(r.url))
            page.route('**/assets/js/pointcloud-viewer.js', instrument)
            page.goto(base + path)
            wait_ready(page)
            initial = snapshot(page)
            assert initial['vertices'] == 453253 and initial['geometryCount'] == 1
            assert initial['size'] == 2 and not initial['attenuation']
            # r185 PLYLoader stores linear colors in normalized uint8 attributes.
            for encoded, srgb in zip(initial['color'], [119, 18, 16]):
                value = srgb / 255
                linear = value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4
                assert abs(encoded / 255 - linear) <= 1 / 255
            assert_close(initial['direction'], [3.2047461e-5, -5.3081767e-6, -1], 1e-8)
            assert initial['ratio'] == (2 if mobile else 1)
            first_ms = page.evaluate('window.__firstDraw')
            assert page.locator('#tab-vggt').get_attribute('aria-selected') == 'true'
            assert page.locator('canvas').count() == 1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert 320 <= page.locator('canvas').bounding_box()['height'] <= 680
            page.screenshot(path=str(OUT / ('mobile-vggt.png' if mobile else 'desktop-vggt.png')))
            before = snapshot(page)
            page.wait_for_timeout(400)
            assert snapshot(page)['draws'] == before['draws'], 'Idle rendering'
            if mobile: touch(page)
            else: drag(page)
            rotated = snapshot(page)
            assert rotated['position'] != before['position'], 'Rotation did not move camera'
            assert_close(rotated['distance'], before['distance'])
            assert_close(rotated['target'], before['target'])
            if mobile:
                touch(page, two=True)
            else:
                drag(page, 'right')
                drag(page, 'middle')
                page.mouse.wheel(0, 120)
            assert_close(snapshot(page)['position'], rotated['position'])
            assert_close(snapshot(page)['distance'], rotated['distance'])
            page.locator('#tab-hdf').click()
            inactive = snapshot(page)
            page.wait_for_timeout(400)
            assert snapshot(page)['draws'] == inactive['draws']
            page.locator('[data-result-next]').click()
            assert page.locator('[data-sample-index="1"]').get_attribute('aria-pressed') == 'true'
            page.locator('[data-result-prev]').click()
            assert page.locator('[data-sample-index="0"]').get_attribute('aria-pressed') == 'true'
            page.locator('[data-sample-index="5"]').click()
            page.locator('[data-comparison-range]').fill('31')
            page.locator('[data-comparison-range]').dispatch_event('input')
            page.locator('[data-lang-button="kr"]').click()
            assert page.locator('#tab-hdf').get_attribute('aria-selected') == 'true'
            assert page.locator('[data-sample-index="5"]').get_attribute('aria-pressed') == 'true'
            for index in range(8):
                page.locator(f'[data-sample-index="{index}"]').click()
                page.wait_for_function("Array.from(document.querySelectorAll('.comparison-media img')).every(i => i.complete && i.naturalWidth > 0)")
            page.locator('[data-sample-index="5"]').click()
            page.locator('.comparison-section').scroll_into_view_if_needed()
            page.screenshot(path=str(OUT / ('mobile-hdf-kr.png' if mobile else 'desktop-hdf-kr.png')))
            for _ in range(4):
                page.locator('#tab-vggt').click()
                page.locator('#tab-hdf').click()
            assert page.locator('[data-comparison-range]').input_value() == '31'
            assert page.locator('[data-sample-index="5"]').get_attribute('aria-pressed') == 'true'
            page.locator('#tab-hdf').focus()
            page.keyboard.press('ArrowLeft')
            assert page.locator('#tab-vggt').evaluate('(e) => e === document.activeElement')
            assert_close(snapshot(page)['position'], rotated['position'])
            assert '453,253점' in page.locator('[data-viewer-status]').inner_text()
            page.keyboard.press('End')
            assert page.locator('#tab-hdf').get_attribute('aria-selected') == 'true'
            page.keyboard.press('Home')
            assert page.locator('#tab-vggt').get_attribute('aria-selected') == 'true'
            page.locator('[data-pointcloud-viewer]').scroll_into_view_if_needed()
            pre_resize = snapshot(page)
            page.set_viewport_size({'width':844 if mobile else 1000, 'height':390 if mobile else 900})
            page.locator('[data-pointcloud-viewer]').scroll_into_view_if_needed()
            resized = snapshot(page)
            assert_close(resized['direction'], pre_resize['direction'])
            assert_close(resized['target'], pre_resize['target'])
            assert resized['near'] > 0 and resized['far'] > resized['distance']
            page.locator('footer').scroll_into_view_if_needed()
            offscreen = snapshot(page)
            page.wait_for_timeout(400)
            assert snapshot(page)['draws'] == offscreen['draws']
            assert not offscreen['enabled']
            page.locator('[data-pointcloud-viewer]').scroll_into_view_if_needed()
            settle(page)
            page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: true }); document.dispatchEvent(new Event('visibilitychange'))")
            hidden = snapshot(page)
            page.set_viewport_size({'width':600,'height':800})
            settle(page)
            assert snapshot(page)['draws'] == hidden['draws']
            page.evaluate("delete document.hidden; document.dispatchEvent(new Event('visibilitychange'))")
            page.locator('[data-pointcloud-viewer]').scroll_into_view_if_needed()
            settle(page)
            assert snapshot(page)['draws'] > hidden['draws']
            assert len([r for r in requests if r.endswith('pointcloud.ply')]) == 1
            assert page.locator('canvas').count() == 1
            page.evaluate("document.querySelector('[data-pointcloud-viewer]').remove()")
            settle(page)
            assert page.evaluate('window.__qa().disposed')
            assert page.locator('canvas').count() == 0
            results.append({'path':path,'mobile':mobile,'first_display_ms':round(first_ms,1),'initial':initial,'checks':'rotation, fixed distance/target, disabled zoom/pan, tabs, keyboard, languages, all HDF samples, resize, idle/inactive/offscreen/hidden, one fetch/canvas, removal cleanup'})
            context.close()

        # Slow PLY: switch tabs/language while loading, then complete once.
        context = browser.new_context(viewport={'width':1440,'height':1100})
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.route('**/assets/js/pointcloud-viewer.js', instrument)
        pending = []
        page.route('**/pointcloud.ply', lambda route: pending.append(route))
        page.goto(base)
        page.wait_for_function("document.querySelector('canvas') !== null")
        page.locator('#tab-hdf').click()
        page.locator('[data-lang-button="kr"]').click()
        assert pending
        pending.pop().fulfill(path=str(ROOT / 'assets/data/vggt/pointcloud.ply'))
        page.wait_for_function("window.__qa().state === 'ready'")
        assert snapshot(page)['draws'] == 0
        page.locator('#tab-vggt').click()
        wait_ready(page)
        assert '453,253점' in page.locator('[data-viewer-status]').inner_text()
        context.close()
        results.append({'loading_switch':'passed'})

        # Abort and remove during loading; completion must not resurrect a canvas.
        context = browser.new_context()
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.route('**/assets/js/pointcloud-viewer.js', instrument)
        pending = []
        page.route('**/pointcloud.ply', lambda route: pending.append(route))
        page.goto(base)
        page.wait_for_function("window.__qa !== undefined")
        page.evaluate("document.querySelector('[data-pointcloud-viewer]').remove()")
        settle(page)
        assert page.evaluate('window.__qa().disposed')
        for route in pending:
            route.fulfill(path=str(ROOT / 'assets/data/vggt/pointcloud.ply'))
        settle(page)
        assert page.locator('canvas').count() == 0
        context.close()
        results.append({'loading_disposal':'passed'})

        for failure in ['404', 'corrupt', 'module', 'webgl', 'contextlost']:
            context = browser.new_context()
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            if failure == '404':
                page.route('**/pointcloud.ply', lambda route: route.fulfill(status=404,body='missing'))
            elif failure == 'corrupt':
                corrupt = bytearray((ROOT / 'assets/data/vggt/pointcloud.ply').read_bytes())
                corrupt[-1] ^= 1
                page.route('**/pointcloud.ply', lambda route: route.fulfill(body=bytes(corrupt)))
            elif failure == 'module':
                page.route('**/vendor/three/PLYLoader.js', lambda route: route.fulfill(status=404,body='missing'))
            elif failure == 'webgl':
                page.add_init_script("const original = HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext = function(type,...args) { return type.includes('webgl') ? null : original.call(this,type,...args); }")
            page.goto(base + '/preview/')
            if failure == 'contextlost':
                page.wait_for_function("document.querySelector('[data-pointcloud-viewer]').dataset.viewerState === 'ready'")
                page.evaluate("document.querySelector('canvas').getContext('webgl2').getExtension('WEBGL_lose_context').loseContext()")
            state = 'file' if failure in ['404','corrupt'] else ('webgl' if failure == 'contextlost' else failure)
            page.wait_for_function("s => document.querySelector('[data-pointcloud-viewer]').dataset.viewerState === s", arg=state)
            en = page.locator('[data-viewer-status]').inner_text()
            page.locator('[data-lang-button="kr"]').click()
            kr = page.locator('[data-viewer-status]').inner_text()
            assert en != kr and len(kr) > 10
            page.locator('#tab-hdf').click()
            page.locator('[data-result-next]').click()
            assert page.locator('[data-sample-index="1"]').get_attribute('aria-pressed') == 'true'
            results.append({'failure':failure,'en':en,'kr':kr,'hdf':'working'})
            context.close()
        browser.close()
    server.shutdown()
    report = {'browser':version,'renderer':'headless Chromium / SwiftShader','results':results,'unhandled_errors':errors}
    (OUT / 'browser-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    assert not errors, errors
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__ == '__main__':
    run()
