import copy
import datetime
import os
import re
import yaml

import flask
import jinja2

app = flask.Flask(__name__)


def get_eps(hide_hidden=False):
    podcast = yaml.load(app.open_resource('static/podcast.yaml'))
    eps = podcast['episodes']
    for ep in eps:
        ep['air_datetime'] = datetime.datetime.strptime(
            ep['air_datetime'], "%Y-%m-%dT%H:%M:%S" )
        ep['pub_datetime'] = datetime.datetime.strptime(
            ep['pub_datetime'], "%Y-%m-%dT%H:%M:%S" )
    eps = {x['url'].split('hgp/hgp-')[1].split('.mp3')[0]: x for x in eps}
    if hide_hidden:
        eps = {k: v for k, v in eps.items() if not v.get('hidden')}
    for k, v in eps.items():
        v['key'] = k
    return eps


@app.route('/')
def index():
    podcast = yaml.load(app.open_resource('static/podcast.yaml'))
    return flask.render_template('index.html', podcast=podcast)


@app.route('/eps/')
def episodes():
    return flask.render_template('episodes.html',
            episodes=get_eps(hide_hidden=True), hideblurb=True)


@app.route('/ep/<date>.html')
def episode(date):
    eps = get_eps()
    return flask.render_template('episode.html', episode=eps[date])


@app.route('/playlist.html')
def playlist():
    podcast = yaml.load(app.open_resource('static/podcast.yaml'))
    return flask.render_template('playlist.html', podcast=podcast)


@app.route('/feed.xml')
def podcast_feed():
    def extract_copyright_years(podcast):
        years = [(x['air_datetime']).year for x in podcast['episodes']]
        min_year = min(years)
        max_year = max(years)
        if min_year != max_year:
            return '{}-{}'.format(min_year, max_year)
        else:
            return str(max_year)

    def parse_datetime(datetime_string):
        # aka 2015-01-09T19:30:00
        return datetime.datetime(*map(int,
                                      re.split('[^\d]',
                                      datetime_string)[:-1]))

    def parse_podcast_years(podcast):
        podcast = copy.deepcopy(podcast)
        for episode in podcast['episodes']:
            episode['air_datetime'] = parse_datetime(episode['air_datetime'])
            episode['pub_datetime'] = parse_datetime(episode['pub_datetime'])
        return podcast

    podcast = yaml.load(app.open_resource('static/podcast.yaml'))
    podcast = parse_podcast_years(podcast)
    copyright_years = extract_copyright_years(podcast)
    response = flask.make_response(flask.render_template('podcast.xml',
                                     podcast=podcast,
                                     copyright_years=copyright_years))
    response.mimetype = "application/xml"
    return response


@app.route('/humans.txt')
def humans_txt():
    return flask.send_from_directory(app.static_folder, 'humans.txt')


@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('404.html'), 404

# Some notes from http://stevenloria.com/hosting-static-flask-sites-for-free-on-github-pages/
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR))
# In order to deploy to Github pages, you must build the static files to
# the project root
app.config['FREEZER_DESTINATION'] = PROJECT_ROOT
app.config['FREEZER_BASE_URL'] = "http://localhost/"
app.config['FREEZER_REMOVE_EXTRA_FILES'] = False  # IMPORTANT: If this is True, all app files
                                    # will be deleted when you run the freezer

if __name__ == '__main__':
    app.run(debug=True)
