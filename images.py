import os.path
import os
import urllib.parse
import requests


class ImageDownloader:
    def __init__(self, folder: str):
        self.folder = folder
        self.relative_path = os.path.relpath(folder, os.path.curdir)

        if not os.path.exists(self.relative_path):
            os.mkdir(self.relative_path)

    def fetch_image(self, url):
        parsed = urllib.parse.urlparse(url)

        path = urllib.parse.unquote(parsed.path)
        filename = os.path.basename(path)
        rel_path = self.relative_path + "/" + filename

        if not os.path.exists(rel_path):
            r = requests.get(url, stream=True)

            with open(rel_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=4096):
                    f.write(chunk)

        return rel_path
