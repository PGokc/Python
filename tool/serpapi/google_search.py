from serpapi import GoogleSearch

query = GoogleSearch({"q": "coffee", "location": "Shanghai,China"})
data = query.get_json()
print(data)