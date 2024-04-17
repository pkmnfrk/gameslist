from io import TextIOWrapper
import os.path
import os

from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gametranslator import GameTranslator
from images import ImageDownloader

translator = GameTranslator()
downloader = ImageDownloader("images")


class ListGame:
    def __init__(self, row):
        self.title = row[0]
        if len(row) <= 1 or int(row[1]) > 1000:
            self.votes = None
        else:
            self.votes = int(row[1])
        if len(row) <= 2 or not row[2]:
            self.date_suggested = "2000-01-01"
        else:
            self.date_suggested = row[2]
        self.attribution = None if len(row) <= 3 else row[3]
        self.provider = None if len(row) <= 4 else row[4]
        self.notes = None if len(row) <= 5 else row[5]
        self.completed = None if len(row) <= 6 else row[6]


def write_game(f: TextIOWrapper, moby_game, game: ListGame):
    image_path = None
    if moby_game["cover"]:
        image_path = downloader.fetch_image(moby_game["cover"])
    desc = moby_game["description"] if moby_game["description"] else ""
    f.write('        <div class="game">\n')
    if image_path:
        f.write(
            f'          <div class="realimage" style="background-image: url({image_path})"></div>\n'
        )
    else:
        f.write('          <div class="fakeimage">?</div>\n')
    f.write(f"          <h2>{moby_game['title']}</h2>\n")
    if game.votes:
        f.write(
            f"          <p class=\"votes\">Suggested by {game.attribution} on {game.date_suggested} <span class=\"votesreal\">({game.votes} vote{'' if game.votes == 1 else 's'})</span></p>"
        )
        pass
    else:
        f.write('          <p class="votes">Streamer chosen</p>')
    f.write(f'          <div class="description">{desc}</div>')
    f.write("        </div>\n")


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1gNaQwGtPC2ioVR4AcSIzeGAGGOX-O-DU-jgioO2dN2M"
SAMPLE_RANGE_NAME = "raw schedule!A:G"


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    translator.load()

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        values = list(ListGame(row) for row in values[1:] if row[0])

        values = list(
            sorted(
                values,
                key=lambda g: (
                    (10000 - g.votes) if g.votes else 999999,
                    g.date_suggested,
                ),
            )
        )

        # sort the data
        god_chosen = list(g for g in values if not g.votes)
        pleb_chosen = list(g for g in values if g.votes)

        final_list: List[ListGame] = list()
        completed_list: List[ListGame] = list()

        while god_chosen or pleb_chosen:
            # first pull an item from god list
            if god_chosen:
                g = god_chosen.pop(0)
                # but only if not completed
                if not g.completed:
                    final_list.append(g)
                else:
                    completed_list.append(g)

            # same thing, but pleb
            if pleb_chosen:
                g = pleb_chosen.pop(0)
                if not g.completed:
                    final_list.append(g)
                else:
                    completed_list.append(g)

        with open("schedule.html", "w", encoding="utf-8") as f:
            f.writelines(
                [
                    "<!doctype html>\n",
                    "<html>\n",
                    "  <head>\n",
                    "    <title>Upcoming Games List</title>\n",
                    '    <link rel="stylesheet" href="style.css"></link>\n',
                    "  </head>\n",
                    "  <body>\n",
                    "    <h1>Upcoming Games</h1>\n",
                    '    <div class="gamelist">\n',
                ]
            )

            for game in final_list:
                moby_game = translator.translate(game.title)
                write_game(f, moby_game, game)
            f.write("    </div>\n")

            if completed_list:
                f.write("    <h1>Completed Games</h1>\n")
                f.write('    <div class="gamelist">\n')
                for game in completed_list:
                    moby_game = translator.translate(game.title)
                    write_game(f, moby_game, game)

                f.write("    </div>\n")

            f.writelines(["  </body>\n", "</html>\n"])

    except HttpError as err:
        print(err)
    finally:
        translator.save()


if __name__ == "__main__":
    main()
