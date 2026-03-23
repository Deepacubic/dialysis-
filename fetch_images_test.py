import urllib.request
import re

def get_unsplash_url(query):
    try:
        url = f"https://unsplash.com/s/photos/{urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        # find the first high res image link
        match = re.search(r'"regular":"(https://images\.unsplash\.com/photo-[^"]+?)"', html)
        if match:
            return match.group(1)
        # Try finding srcset as fallback
        match = re.search(r'srcset="(https://images\.unsplash\.com/photo-[^"]+?\bw=1080\b[^"]*)"', html)
        if match:
             return match.group(1).split(" ")[0]
        return None
    except Exception as e:
        print(f"Error fetching {query}: {e}")
        return None

print(get_unsplash_url("guava fruit"))
