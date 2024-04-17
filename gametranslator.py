import os.path
import json
from moby import MobyGames


class GameTranslator:
    def __init__(self):
        self.games = {}
        self.moby = MobyGames()

    def translate(self, game):
        if not game in self.games:
            games = self.moby.get_game_for_title(game)
            if not games:
                print(
                    f"Unable to resolve {game} to a game, try double checking punctuation"
                )
            else:
                # look for a suitable game
                chosen_game = None
                for g in games:
                    if g["title"].lower() == game.lower():
                        chosen_game = g
                        break

                if not chosen_game:
                    chosen_game = games[0]

                info = {
                    "id": chosen_game["game_id"],
                    "description": chosen_game["description"],
                    "title": chosen_game["title"],
                }

                if chosen_game["sample_cover"] and chosen_game["sample_cover"]["image"]:
                    info["cover"] = chosen_game["sample_cover"]["image"]
                else:
                    info["cover"] = None

                self.games[game] = info

        if not game in self.games:
            self.games[game] = {
                "id": "unknown",
                "description": "",
                "title": game,
                "cover": None,
            }

        return self.games[game]

    def load(self):
        if os.path.exists("games.json"):
            try:
                with open("games.json") as f:
                    self.games = json.load(f)
            except Exception as e:
                print(f"Couldn't load game list: {e}")

    def save(self):
        with open("games.json", "w") as f:
            json.dump(self.games, f, indent=2)
