import urllib.request
import urllib.error

def check_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        return res.status == 200
    except urllib.error.URLError as e:
        print(f"Error checking {url}: {e}")
        return False

print(check_url("https://loremflickr.com/500/500/guava,fruit,food"))
