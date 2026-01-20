from .google import google_main
from .meta import meta_main
from loguru import logger
import json


def main(request):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'request.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        request_json: dict = json.load(f)

    platform: str = request_json.get("platform")

    if platform == "google":
        return google_main(request)

    if platform == "meta":
        return meta_main(request)


class MakeRequest:
    def __init__(self):
        self.request = {
            "secret_id": "meta__cadastra-dea-api",
            "project_id": "76816773014",
            "force_refresh": "True",
            "platform": "meta",
        }

    def get_json(self):
        return self.request


if __name__ == "__main__":
    new_request = MakeRequest()
    main(new_request)
