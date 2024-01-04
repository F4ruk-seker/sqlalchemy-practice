import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class Content:
    def __init__(self, _type: str, special: str):
        self.type = _type
        self.special = special


class UrlSharing:
    def __init__(self, url):
        self.url = url
        self.ua = UserAgent()
        self.parsed_url = None

    def isUrl(self):
        try:
            self.parsed_url = urlparse(self.url)
            return True
        except:
            return False

    def get_content(self):
        try:
            content_types = [Content('title', 'h1'), Content('description', 'p'), Content('image', 'img')]
            response = requests.get(self.url,
                                    # headers={'user-agent':self.ua.random},
                                    timeout=10)
            html = BeautifulSoup(response.text, 'html.parser')
            result = {}
            for content in content_types:
                result[content.type] = None
                if html.find('meta', property='og:' + content.type):
                    result[content.type] = html.find('meta', property='og:' + content.type).get('content')
                elif html.find('meta', property='twitter:' + content.type):
                    result[content.type] = html.find('meta', property='twitter:' + content.type).get('content')
                else:
                    if content.type == 'image':
                        if html.find(content.special, src=True):
                            result[content.type] = html.find(content.special).get('src')
                        else:
                            if html.find(content.special):
                                result[content.type] = html.find(content.special).string
                    elif content.type == 'title':
                        result[content.type] = html.title.string
            return result
        except requests.exceptions.Timeout:
            print('argo')
            pass
        except Exception as e:
            print(e)
            pass


# # url = UrlSharing('https://open.spotify.com/track/6qrAFnjBZfEd4jbCaKpf5w?go=1&sp_cid=2d4be8533a6c75e0b8cdd23f00a2a464&utm_source=embed_player_p&utm_medium=desktop&nd=1')
url = UrlSharing(input('url : '))
# url = UrlSharing('http://localhost:8080/')
print(url.isUrl())
print(url.get_content())

