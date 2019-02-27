import os
import json

from instagram_private_api import Client, ClientError, ClientLoginError, ClientLoginRequiredError, \
    ClientCookieExpiredError
# from instagram_web_api import Client, ClientCompatPatch, ClientError, ClientLoginError, ClientCookieExpiredError

from InstagramFinder.common import onlogin_callback, from_json


class InstagramFinder:
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

    def find_split(self, instagram_account):
        # Выполянет поиск пересечений
        result_followers = []
        for account in instagram_account:
            rank_token = Client.generate_uuid()
            user_id = self.api.username_info(account)["user"]["pk"]
            followers = []
            results = self.api.user_followers(user_id, rank_token)
            followers.extend(results.get('users', []))

            next_max_id = results.get('next_max_id')
            while next_max_id:
                results = self.api.user_followers(user_id, rank_token=rank_token, max_id=next_max_id)
                followers.extend(results.get('users', []))
                if len(followers) >= 200:  # get only first 600 or so
                    break
                next_max_id = results.get('next_max_id')

            followers.sort(key=lambda x: x['pk'])
            result_followers.append(followers)

        split = []
        for f_list in result_followers:
            for item in f_list:
                if item in split:
                    continue
                find = 0
                for f in result_followers:
                    if item in f:
                        find += 1
                if find == len(result_followers):
                    split.append(item)
        return split

    def add_photo(self, array_split):
        for account in array_split:
            if not account["is_private"]:
                media = self.api.user_feed(account["pk"])
                account["photo"] = media["items"]
            else:
                account["photo"] = []
        return array_split

    def save_to_file(self, array_split):
        html_str = """
        <table border=1>
             <tr>
               <th>Kiska</th>
               <th>FullName</th>
               <th>URL</th>
               <th>User</th>
               <th>Photo</th>
             </tr>
             <indent>
        
               """

        html_end = """
             </indent>
        </table>
        """
        table = ""
        for account in array_split:
            table += "<tr>"
            table += str.format("<td>{0}</td>", account["username"])
            table += str.format("<td>{0}</td>", account["full_name"])
            table += str.format("<td><a href=http://instagram.com/{0}/>{0}</a></td>", account["username"])
            table += """<td> <img src=""" + account["profile_pic_url"] + """ width="255" height="255" alt="lorem"> </td>"""

            table += "<td>"
            index = 0
            for item in account["photo"]:
                try:
                    table += """<img src=""" + item["image_versions2"]["candidates"][0]["url"] + """ width="255" height="255" alt="lorem">"""
                except KeyError:
                    table += """<img src=""" + item["carousel_media"][0]["image_versions2"]["candidates"][0][
                        "url"] + """ width="255" height="255" alt="lorem">"""

                index += 1
                if index > 4:
                    break

            table += "</td>"

            table += "</tr>"

        with open('result.html', 'w', encoding="utf-8") as file:
            file.write(html_str + table + html_end)
        # Сохраним в HTML +
