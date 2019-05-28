import datetime
import logging
import os
import json

from instagram_private_api import Client, ClientError, ClientLoginError, ClientLoginRequiredError, \
    ClientCookieExpiredError
# from instagram_web_api import Client, ClientCompatPatch, ClientError, ClientLoginError, ClientCookieExpiredError

from InstagramFinder.common import onlogin_callback, from_json


class InstagramGeoFinder:
    def __init__(self):
        username = os.environ["instagram_username"]
        password = os.environ["instagram_password"]
        self.settings_file = "instagram_client"

        device_id = None
        try:
            if not os.path.isfile(self.settings_file):
                self.api = Client(auto_patch=True, authenticate=True, username=username, password=password,
                                  on_login=lambda x: onlogin_callback(x, self.settings_file))
            else:
                with open(self.settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=from_json)
                print('Reusing settings: {0!s}'.format(self.settings_file))

                device_id = cached_settings.get('device_id')
                # reuse auth settings
                self.api = Client(
                    username=username, password=password,
                    settings=cached_settings)

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:

            # Login expired
            # Do relogin but use default ua, keys and such
            self.api = Client(
                username=username, password=password,
                device_id=device_id,
                on_login=lambda x: onlogin_callback(x, self.settings_file))

    def find_geo(self, location_id, count):
        result_photo = []
        rank_token = Client.generate_uuid()
        location_info = self.api.location_info(location_id)
        self.file_name = location_info["location"]["name"]


        result_location = self.api.location_section(location_id, rank_token, tab='recent')

        for item in result_location["sections"]:
            result_photo.append(item)

        next_max_id = result_location["next_max_id"]

        while next_max_id:
            result_location = self.api.location_section(location_id, rank_token, tab='recent', max_id=next_max_id)

            for item in result_location["sections"]:
                result_photo.append(item)

            if len(result_photo) >= count:  # get only first 600 or so
                break
            try:
                next_max_id = result_location["next_max_id"]
            except KeyError:
                break

        logging.info(len(result_photo))
        return result_photo

    def get_filename(self):
        filename = "instagram_%s" % self.file_name

        filename += ".html"
        return filename

    def save_to_file(self, array_photo):
        logging.info("Save to html")
        html_str = """
                <!DOCTYPE html>
                <html>
                 <head>
                  <meta charset="utf-8">
                  <title>Kiski Finder</title>
                 </head>
                 <body> 
                <table border=1>
                     <tr>
                      <th>Kiska</th>
                      <th>FullName</th>
                       <th>Time and Description</th>
                       
                      
                       <th>User</th>
                       <th>Photo</th>
                     </tr>
                     <indent>

                       """

        html_end = """
                     </indent>
                </table>
                 </body>
                </html>
                """
        table = ""
        for layout in array_photo:
            for item in layout["layout_content"]["medias"]:
                try:
                    time = int(item["media"]["caption"]["created_at"])
                    photo_time = datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
                    photo_time += " </br> %s" % item["media"]["caption"]["text"]
                except TypeError:
                    photo_time = "-"

                table += "<tr>"
                table += str.format("<td><a href=http://instagram.com/{0}/>{0}</a></td>",
                                    item["media"]["user"]["username"])
                table += str.format("<td>{0}</td>", item["media"]["user"]["full_name"])
                table += str.format('<td width="200" style="word-break: break-all;">{0}</td>', photo_time)


                table += """<td> <img src=""" + item["media"]["user"]["profile_pic_url"] + """ width="255" height="255" alt="lorem"> </td>"""

                table += "<td>"
                index = 0

                try:
                    table += """<img src=""" + item["media"]["image_versions2"]["candidates"][0][
                        "url"] + """ width="255" height="255" alt="lorem">"""
                except KeyError:
                    table += """<img src=""" + item["media"]["carousel_media"][0]["image_versions2"]["candidates"][0][
                        "url"] + """ width="255" height="255" alt="lorem">"""

                index += 1
                if index > 10:
                    break

            table += "</td>"

            table += "</tr>"

        if not os.path.isdir("result_html"):
            os.mkdir("result_html")

        with open("result_html//" + self.get_filename(), 'w', encoding="utf-8") as file:
            file.write(html_str + table + html_end)
        # Сохраним в HTML +

