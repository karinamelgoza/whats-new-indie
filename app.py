from flask import Flask, render_template

from igdb.wrapper import IGDBWrapper

import json
import config

app = Flask(__name__)

wrapper = IGDBWrapper(config.client_id,
                      config.access_token)


@app.route('/')
def homepage():

    byte_array = wrapper.api_request(
        'games', 'fields name, cover.url, videos.video_id; where release_dates.date > 1627776000 & release_dates.date < 1630454400 & genres = (32) & platforms= (130); limit 10;')

    results = json.loads(byte_array)
    # for i in results:
    #     if i.get('videos'):
    #         video_list = i.get('videos')
    #         video_id = video_list[0].get('video_id')
    #         video_url = f"https://www.youtube.com/watch?v={video_id}"

    return render_template('homepage.html', results=results)


# @app.route('/show_games')
# def get_games():
#     byte_array = wrapper.api_request(
#         'games', 'fields name; where release_dates.date > 1627776000 & release_dates.date < 1630454400 & genres = (32) & platforms= (130); limit 10;')

#     results = json.loads(byte_array)

#     print(results)
    # return byte_array


if __name__ == '__main__':
    app.run(debug=True)
    # get_games()
