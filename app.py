from flask import Flask, render_template

from igdb.wrapper import IGDBWrapper

import json
import config
import requests

app = Flask(__name__)

wrapper = IGDBWrapper(config.client_id,
                      config.access_token)


@app.route('/')
def homepage():

    response = requests.get(
        f"https://api.rawg.io/api/games?dates=2021-08-01,2021-08-31&key={config.key}&platforms=18,1,7,187,186,3,21&genres=51&page_size=50&page=1&ordering=released")

    results_rawg = response.json()

    byte_array = wrapper.api_request(
        'games', 'fields name, cover.url, videos.video_id, release_dates.human; where first_release_date < 1627776000 &release_dates.date > 1627776000 & release_dates.date < 1630454400 & genres = (32) & platforms= (130); limit 60;')

    results = json.loads(byte_array)

    return render_template('homepage.html', results=results, results_rawg=results_rawg['results'],)


if __name__ == '__main__':
    app.run(debug=True)
    # get_games()
