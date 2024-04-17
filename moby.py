import os.path
import json
import requests
import time
from typing import List, Dict


class MobyGames:
    base_url = "https://api.mobygames.com/v1"

    def __init__(self):
        if os.path.exists("moby.json"):
            with open("moby.json") as f:
                obj = json.load(f)
                self.api_key = obj["api_key"]
        else:
            raise Exception("No Moby API Key")
        self.last_call = 0

    def get_game_for_title(self, title) -> List[Dict]:
        arg = {
            "format": "normal",
            "title": title,
        }

        results = self.make_api_call("GET", "/games", arg)
        return results["games"]

    def make_api_call(self, method, url, args):
        now = time.time()
        limit_time = now - 2

        if self.last_call > limit_time:
            print("Sleeping to respect MobyGames API rate limit...")
            time.sleep(1)

        self.last_call = time.time()

        resp = requests.request(
            method, self.base_url + url, params={**args, "api_key": self.api_key}
        )

        resp.raise_for_status()

        return resp.json()


if __name__ == "__main__":
    test = MobyGames()
    games = test.get_game_for_title("Another World")
    for t in games:
        print(t["game_id"], t["title"])
