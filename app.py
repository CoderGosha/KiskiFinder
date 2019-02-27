import logging

from InstagramFinder.instagram_finder import InstagramFinder
from loggerinitializer import initialize_logger

if __name__ == '__main__':
    initialize_logger("log")
    logging.info("Starting Kiski Finder...")

    instagram_account = ["easeisease", "dorozhnij"]

    worker = InstagramFinder()
    array_spit = worker.find_split(instagram_account)
    array_spit = worker.add_photo(array_spit)
    worker.save_to_file(array_spit, worker.get_filename(instagram_account))
