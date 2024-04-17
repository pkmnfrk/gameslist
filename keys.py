from io import TextIOWrapper
import os.path
import os

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
        self.title = str(row[0])
        self.platform = str(row[1])


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
    f.write(f"          <p>Platform: {game.platform}</p>\n")
    f.write(f'          <div class="description">{desc}</div>')
    f.write("        </div>\n")


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1YKfxIgEyYlPkm0lvzk5wCMz3Kh6X6PK3GbrWGWHD0sA"
SAMPLE_RANGE_NAME = "GAMES!A:B"


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
                key=lambda g: (g.title),
            )
        )

        with open("keys.html", "w", encoding="utf-8") as f:
            f.writelines(
                [
                    "<!doctype html>\n",
                    "<html>\n",
                    "  <head>\n",
                    "    <title>Available Keys for Redemption</title>\n",
                    '    <link rel="stylesheet" href="style.css"></link>\n',
                    "  </head>\n",
                    "  <body>\n",
                    "    <h1>Available Keys</h1>\n",
                    '    <p>If you want a game key, all you have to do is come by a stream (<a href="https://twitch.tv/cdutson">https://twitch.tv/cdutson</a>) and spend some channel points!</p>\n'
                    '    <div class="gamelist">\n',
                ]
            )

            for game in values:
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
