def main():
    # 1. Update sw.js
    with open('public/sw.js', 'r', encoding='utf-8') as f:
        sw = f.read()
    sw = sw.replace("const CACHE_VERSION = 'v1.3.1';", "const CACHE_VERSION = 'v1.3.2';")
    with open('public/sw.js', 'w', encoding='utf-8') as f:
        f.write(sw)
    print("Updated sw.js to v1.3.2")

    # 2. Update index.html
    with open('public/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace('v=20261020_v131', 'v=20261020_v132')
    html = html.replace('v1.3.1', 'v1.3.2')
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated index.html to v1.3.2")

if __name__ == '__main__':
    main()
