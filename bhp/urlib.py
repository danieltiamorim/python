import urllib.request

response = urllib.request.urlopen("https://nasa.gov")
html = response.read()
#html = html.decode("utf-8")

#print(html)
print(type(html))
print(response.status)
print(response.getheaders())

