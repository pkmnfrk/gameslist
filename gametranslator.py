import os.path
import json
from moby import MobyGames


class GameTranslator:
    def __init__(self):
        self.games = {
            "_": "NOTE: If a game is wrong, you have two options. 1. Fix the game name in the source; 2. add/modify an 'override_id' field with the correct id."
        }
        self.moby = MobyGames()

    def translate(self, game):
        if game not in self.games:
            games = self.moby.get_games_for_title(game)
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
                    "override_id": chosen_game["game_id"],
                    "description": chosen_game["description"],
                    "title": chosen_game["title"],
                }

                if chosen_game["sample_cover"] and chosen_game["sample_cover"]["image"]:
                    info["cover"] = chosen_game["sample_cover"]["image"]
                else:
                    info["cover"] = None

                self.games[game] = info

        if game in self.games and "override_id" in self.games[game]:
            if self.games[game]["id"] != self.games[game]["override_id"]:
                chosen_game = self.moby.get_game_for_id(self.games[game]["override_id"])
                info = {
                    "id": chosen_game["game_id"],
                    "override_id": chosen_game["game_id"],
                    "description": chosen_game["description"],
                    "title": chosen_game["title"],
                }

                if chosen_game["sample_cover"] and chosen_game["sample_cover"]["image"]:
                    info["cover"] = chosen_game["sample_cover"]["image"]
                else:
                    info["cover"] = None

                self.games[game] = info

        if game not in self.games:
            self.games[game] = {
                "id": "unknown",
                "override_id": "unknown",
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
