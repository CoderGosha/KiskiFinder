import logging

from InstagramFinder.instagram_finder import InstagramFinder
from InstagramFinder.instagram_geo_finder import InstagramGeoFinder
from loggerinitializer import initialize_logger

if __name__ == '__main__':
    initialize_logger("log")
    logging.info("Starting Kiski Finder...")

    instagram_account = ["farangbarspb", "farangbarspb"]

    worker = InstagramGeoFinder()
    array_photo = worker.find_geo("216511113", 1000)

    worker.save_to_file(array_photo)
