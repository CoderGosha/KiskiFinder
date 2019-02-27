from InstagramFinder.instagram_finder import InstagramFinder
from loggerinitializer import initialize_logger

if __name__ == '__main__':
    initialize_logger("log")
    instagram_account = ["sibaristica", "vainskaya"]
    worker = InstagramFinder()
    array_spit = worker.find_split(instagram_account)
    array_spit = worker.add_photo(array_spit)
    worker.save_to_file(array_spit)
