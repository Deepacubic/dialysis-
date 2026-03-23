import urllib.request
import json
import urllib.parse

def get_wiki_image(title):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&titles={urllib.parse.quote(title)}&pithumbsize=500&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(res)
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "thumbnail" in page_data:
                return page_data["thumbnail"]["source"]
    except Exception as e:
        print(f"Error for {title}: {e}")
    return None

print(get_wiki_image("Pear"))
print(get_wiki_image("Grapes"))
print(get_wiki_image("Guava"))
print(get_wiki_image("Capsicum"))
print(get_wiki_image("Custard apple"))
