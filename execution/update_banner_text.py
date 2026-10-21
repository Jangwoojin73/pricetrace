import os

def update():
    old_str = "네이버 쇼핑 공식 카탈로그 실시간 최저가 레이더"
    new_str = "네이버 쇼핑 공식 카탈로그 실시간 레이더"

    # 1. Update index.html
    with open("public/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    if old_str in html:
        html = html.replace(old_str, new_str)
        html = html.replace("v=20261021_v143", "v=20261021_v144")
        with open("public/index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Updated public/index.html")
    else:
        print("old_str already updated in index.html")

    # 2. Update app.js
    with open("public/app.js", "r", encoding="utf-8") as f:
        js = f.read()
    if old_str in js:
        js = js.replace(old_str, new_str)
        with open("public/app.js", "w", encoding="utf-8") as f:
            f.write(js)
        print("Updated public/app.js")
    else:
        print("old_str already updated in app.js")

    # 3. Update sw.js
    with open("public/sw.js", "r", encoding="utf-8") as f:
        sw = f.read()
    if "v1.4.3" in sw:
        sw = sw.replace("v1.4.3", "v1.4.4")
        with open("public/sw.js", "w", encoding="utf-8") as f:
            f.write(sw)
        print("Updated public/sw.js")
    else:
        print("sw.js already updated")

if __name__ == "__main__":
    update()
