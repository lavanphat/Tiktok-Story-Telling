from os import makedirs
from requests import get


class Font:
    def download(self, url: str, output_path: str):
        makedirs(output_path, exist_ok=True)

        font_file = url.split('/')[-1]
        font_path = f"{output_path}/{font_file}"

        response = get(url)
        with open(font_path, "wb") as f:
            f.write(response.content)

        return font_path