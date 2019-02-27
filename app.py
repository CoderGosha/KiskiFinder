from InstagramFinder.instagram_finder import InstagramFinder
from loggerinitializer import initialize_logger

if __name__ == '__main__':
    initialize_logger("log")
    instagram_account = ["sibaristica", "vainskaya"]
    worker = InstagramFinder()
    worker.find_split(instagram_account)
