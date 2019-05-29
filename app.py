import logging

from InstagramFinder.instagram_finder import InstagramFinder
from InstagramFinder.instagram_geo_finder import InstagramGeoFinder
from loggerinitializer import initialize_logger


from flask import Flask
from flask_restplus import Resource, Api
from flask import request, send_from_directory

app = Flask(__name__)
api = Api(app, title="KiskiFinder", version="1.0", description="Kiski Finder create by CoderGosha")


@api.route('/find_location')
@api.param('location_id', 'Location id by Instagram.com')
@api.param('count', 'Count photo (Max=1000)')
class KiskiFiinder(Resource):
    def get(self):
        location_id = request.args.get('location_id', default="1", type=str)
        count = request.args.get('filter', default=20, type=int)
        if count > 1000:
            count = 1000

        worker = InstagramGeoFinder()
        array_photo = worker.find_geo(location_id, count)
        filename = worker.save_to_file(array_photo)
        return {'link': 'http://localhost:5000/' + filename}

    @app.route('/result_html/<path:path>')
    def send_js(path):
        return send_from_directory('result_html', path)


if __name__ == '__main__':
    initialize_logger("log")
    logging.info("Starting Kiski Finder...")
    app.run(debug=True)
