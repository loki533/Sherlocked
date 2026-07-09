from PIL import Image
from PIL.ExifTags import TAGS


class ExifExtractor:

    @staticmethod
    def extract(image_path):

        try:

            image = Image.open(image_path)

            exif = image.getexif()

            data = {}

            for tag, value in exif.items():

                data[TAGS.get(tag, tag)] = value

            return data

        except Exception:

            return {}