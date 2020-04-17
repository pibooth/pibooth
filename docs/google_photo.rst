Setup
-----

Installing python library dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 ::

        $ sudo pip3 install google-auth-oauthlib

Obtaining a Google Photos API key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Obtain a Google Photos API key (Client ID and Client Secret) by following the instructions on \
[Getting started with Google Photos REST APIs](https://developers.google.com/photos/library/guides/get-started)

**NOTE** When selecting your application type in Step 4 of "Request an OAuth 2.0 client ID", please select "Other". There's also no need to carry out step 5 in that section.

Configure Pibooth to use google api
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Save a client_id.json file and open
2. Replace `YOUR_CLIENT_ID` in the client_id.json file with the provided Client ID.
3. Replace `YOUR_CLIENT_SECRET` in the client_id.json file with the provided Client Secret.

``client_id.json``

.. code-block:: json

    {
    "installed":
        {
            "client_id":"YOUR_CLIENT_ID",
            "client_secret":"YOUR_CLIENT_SECRET",
            "auth_uri":"https://accounts.google.com/o/oauth2/auth",
            "token_uri":"https://www.googleapis.com/oauth2/v3/token",
            "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]
        }
    }

4. Replace `'path/to/client_id.json'` on `pibooth_google_photo.py` to the good path of your `client_id.json`
5. Append plugin to pibooth config
6. At first connection allow application to use google photo with open browser windows


``pibooth_google_photo.py``

.. code-block:: python

    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2.credentials import Credentials
    import json
    import os.path
    import pibooth
    from pibooth.utils import LOGGER

    ###########################################################################
    ## HOOK pibooth
    ###########################################################################
    @pibooth.hookimpl
    def pibooth_startup(app):
        app.google_photo = GoogleUpload(client_id='path/to/client_id.json',
                                        credentials=None)

    @pibooth.hookimpl
    def state_processing_exit(app):
        name = app.previous_picture_file
        app.google_photo.upload_photos([name], "Pibooth")

    ###########################################################################
    ## Class
    ###########################################################################
    class GoogleUpload(object):

        def __init__(self, client_id=None, credentials=None):
            self.scopes = ['https://www.googleapis.com/auth/photoslibrary',
                           'https://www.googleapis.com/auth/photoslibrary.sharing']

            # file to store authorization
            self.google_credentials = credentials
            # file with YOUR_CLIENT_ID and YOUR_CLIENT_SECRET generate on google
            self.google_client_id = client_id
            self.credentials = None
            self.session = None
            self.album_id = None
            self.album_name = None
            self._get_authorized_session()

        def _auth(self):
            """open browser to create credentials"""
            flow = InstalledAppFlow.from_client_secrets_file(
                self.google_client_id,
                scopes=self.scopes)

            self.credentials = flow.run_local_server(host='localhost',
                                                     port=8080,
                                                     authorization_prompt_message="",
                                                     success_message='The auth flow is complete; you may close this window.',
                                                     open_browser=True)

        def _get_authorized_session(self):

            # check the default path of save credentials to allow keep None
            if self.google_credentials is None:
                self.google_credentials = os.path.join(os.path.dirname(self.google_client_id) + "/google_credentials.dat")
            # if first instance of application:
            if not os.path.exists(self.google_credentials) or \
                    os.path.getsize(self.google_credentials) == 0:
                self._auth()
                self.session = AuthorizedSession(self.credentials)
                LOGGER.debug("First run of application create credentials file {}".format(self.google_credentials))
                try:
                    self._save_cred()
                except OSError as err:
                    LOGGER.debug("Could not save auth tokens - {0}".format(err))
            else:
                try:
                    self.credentials = Credentials.from_authorized_user_file(self.google_credentials, self.scopes)
                    self.session = AuthorizedSession(self.credentials)
                except ValueError:
                    LOGGER.debug("Error loading auth tokens - Incorrect format")

        def _save_cred(self):
            if self.credentials:
                cred_dict = {
                    'token': self.credentials.token,
                    'refresh_token': self.credentials.refresh_token,
                    'id_token': self.credentials.id_token,
                    'scopes': self.credentials.scopes,
                    'token_uri': self.credentials.token_uri,
                    'client_id': self.credentials.client_id,
                    'client_secret': self.credentials.client_secret
                }

                with open(self.google_credentials, 'w') as f:
                    print(json.dumps(cred_dict), file=f)

        def get_albums(self, appCreatedOnly=False):
            """#Generator to loop through all albums"""
            params = {
                'excludeNonAppCreatedData': appCreatedOnly
            }
            while True:
                albums = self.session.get('https://photoslibrary.googleapis.com/v1/albums', params=params).json()
                LOGGER.debug("Server response: {}".format(albums))
                if 'albums' in albums:
                    for a in albums["albums"]:
                        yield a
                    if 'nextPageToken' in albums:
                        params["pageToken"] = albums["nextPageToken"]
                    else:
                        return
                else:
                    return

        def _create_or_retrieve_album(self):
            """Find albums created by this app to see if one matches album_title"""
            if self.album_name and self.album_id is None:
                for a in self.get_albums(True):
                    if a["title"].lower() == self.album_name.lower():
                        self.album_id = a["id"]
                        LOGGER.info("Uploading into EXISTING photo album -- \'{0}\'".format(self.album_name))
            if self.album_id is None:
                # No matches, create new album
                create_album_body = json.dumps({"album": {"title": self.album_name}})
                # print(create_album_body)
                resp = self.session.post('https://photoslibrary.googleapis.com/v1/albums', create_album_body).json()
                LOGGER.debug("Server response: {}".format(resp))
                if "id" in resp:
                    LOGGER.info("Uploading into NEW photo album -- \'{0}\'".format(self.album_name))
                    self.album_id = resp['id']
                else:
                    LOGGER.error("Could not find or create photo album \'{0}\'.\
                                 Server Response: {1}".format(self.album_name, resp))
                    self.album_id = None

        def upload_photos(self, photo_file_list, album_name):
            self.album_name = album_name
            self._create_or_retrieve_album()

            # interrupt upload if an upload was requested but could not be created
            if self.album_name and not self.album_id:
                LOGGER.error("Interrupt upload see previous error!!!!")
                return

            self.session.headers["Content-type"] = "application/octet-stream"
            self.session.headers["X-Goog-Upload-Protocol"] = "raw"

            for photo_file_name in photo_file_list:

                try:
                    photo_file = open(photo_file_name, mode='rb')
                    photo_bytes = photo_file.read()
                except OSError as err:
                    LOGGER.error("Could not read file \'{0}\' -- {1}".format(photo_file_name, err))
                    continue

                self.session.headers["X-Goog-Upload-File-Name"] = os.path.basename(photo_file_name)

                LOGGER.info("Uploading photo -- \'{}\'".format(photo_file_name))

                upload_token = self.session.post('https://photoslibrary.googleapis.com/v1/uploads', photo_bytes)

                if (upload_token.status_code == 200) and upload_token.content:

                    create_body = json.dumps({"albumId": self.album_id, "newMediaItems": [
                        {"description": "", "simpleMediaItem": {"uploadToken": upload_token.content.decode()}}]}, indent=4)

                    resp = self.session.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
                                             create_body).json()

                    LOGGER.debug("Server response: {}".format(resp))

                    if "newMediaItemResults" in resp:
                        status = resp["newMediaItemResults"][0]["status"]
                        if status.get("code") and (status.get("code") > 0):
                            LOGGER.error("Could not add \'{0}\' to library -- {1}".format(os.path.basename(photo_file_name),
                                                                                          status["message"]))
                        else:
                            LOGGER.info(
                                "Added \'{}\' to library and album \'{}\' ".format(os.path.basename(photo_file_name),
                                                                                   album_name))
                    else:
                        LOGGER.error(
                            "Could not add \'{0}\' to library. Server Response -- {1}".format(
                                os.path.basename(photo_file_name),
                                resp))

                else:
                    LOGGER.error("Could not upload \'{0}\'. Server Response - {1}".format(os.path.basename(photo_file_name),
                                                                                          upload_token))

            try:
                del (self.session.headers["Content-type"])
                del (self.session.headers["X-Goog-Upload-Protocol"])
                del (self.session.headers["X-Goog-Upload-File-Name"])
            except KeyError:
                pass