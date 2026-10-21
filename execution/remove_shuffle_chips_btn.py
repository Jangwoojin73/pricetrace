# -*- coding: utf-8 -*-

def update_files():
    # 1. Update public/index.html
    with open('public/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    btn_start = html.find('          <button \n            type="button" \n            id="shuffleChipsBtn"')
    if btn_start != -1:
        btn_end = html.find('</button>\n', btn_start) + len('</button>\n')
        html = html[:btn_start] + html[btn_end:]
        print("1. Removed shuffleChipsBtn from index.html")
    else:
        print("WARN: shuffleChipsBtn not found in index.html with exact formatting")
        # Alternative search
        idx = html.find('id="shuffleChipsBtn"')
        if idx != -1:
            tag_start = html.rfind('<button', 0, idx)
            tag_end = html.find('</button>', idx) + len('</button>')
            # also remove preceding indentation or trailing newline
            while tag_start > 0 and html[tag_start-1] in ' \t':
                tag_start -= 1
            if tag_end < len(html) and html[tag_end] == '\n':
                tag_end += 1
            html = html[:tag_start] + html[tag_end:]
            print("1. Removed shuffleChipsBtn from index.html (fallback)")

    # Bump version
    html = html.replace('20261021_v145', '20261021_v146')

    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # 2. Update public/style.css
    with open('public/style.css', 'r', encoding='utf-8') as f:
        css = f.read()

    css_target = '''#shuffleChipsBtn {
  color: #ffffff !important;
  background-color: rgba(255, 255, 255, 0.22) !important;
}'''
    if css_target in css:
        css = css.replace(css_target + '\n', '')
        css = css.replace(css_target, '')
        print("2. Removed #shuffleChipsBtn from style.css")
        with open('public/style.css', 'w', encoding='utf-8') as f:
            f.write(css)

    # 3. Update public/sw.js
    with open('public/sw.js', 'r', encoding='utf-8') as f:
        sw = f.read()

    sw = sw.replace("const CACHE_VERSION = 'v1.4.5';", "const CACHE_VERSION = 'v1.4.6';")
    with open('public/sw.js', 'w', encoding='utf-8') as f:
        f.write(sw)
    print("3. Bumped CACHE_VERSION in sw.js to v1.4.6")

if __name__ == '__main__':
    update_files()
