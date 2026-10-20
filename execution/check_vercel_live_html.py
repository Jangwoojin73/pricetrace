import urllib.request
import re

url = 'https://pricetrace-nu.vercel.app/'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)'})
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
    print('Vercel HTML fetched, length:', len(html))
    
    # Check status-bar-style
    status_bar_match = re.search(r'apple-mobile-web-app-status-bar-style[^>]*', html)
    print('Status bar style in Vercel:', status_bar_match.group(0) if status_bar_match else 'Not found')
    
    # Check topLiveBanner
    print('topLiveBanner in Vercel:', 'topLiveBanner' in html)
    
    # Check header class
    header_match = re.search(r'<header[^>]*>', html)
    print('Header in Vercel:', header_match.group(0) if header_match else 'Not found')
    
    # Check style.css version or contents
    css_match = re.search(r'style\.css\?[^\"\']+', html)
    print('CSS link in Vercel:', css_match.group(0) if css_match else 'Not found')

    # Fetch style.css directly from Vercel
    css_url = 'https://pricetrace-nu.vercel.app/style.css'
    with urllib.request.urlopen(css_url) as resp:
        css = resp.read().decode('utf-8')
    print('style.css fetched, length:', len(css))
    print('topLiveBanner in Vercel style.css:', '#topLiveBanner' in css)

    # Check service worker
    sw_url = 'https://pricetrace-nu.vercel.app/sw.js'
    try:
        with urllib.request.urlopen(sw_url) as resp:
            sw = resp.read().decode('utf-8')
        print('sw.js exists, length:', len(sw))
    except Exception as e:
        print('sw.js check:', e)

except Exception as e:
    print('Error fetching Vercel:', e)

# Check sw.js CACHE_VERSION
with urllib.request.urlopen('https://pricetrace-nu.vercel.app/sw.js') as resp:
    sw = resp.read().decode('utf-8')
for line in sw.splitlines():
    if 'CACHE_VERSION' in line:
        print('Live Vercel line:', line)
