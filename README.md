## About the project
This project is a simple command-line utility script to create monthly Spotify playlists based on your recent listening.

The script uses your specific Spotify credentials (obtained through SSO) to determine your recently listened songs and compiles a playlist out of all of them.

### Prerequisites
    * Python3

    ```pip install: ```
    * requests
    * os
    * json
    * base64
    * datetime

### Usage
You will need to register an application in Spotify's Developer console. From this, you will receive a client_secret and client_id for your application. These values are used in obtaining Spotify SSO credentials. 

The refresh token is obtained using the client_secret and client_id specific to your application. This is best obtained using Postman - a REST API testing tool.

A quick guide on how to obtain the refresh token for your application can be found [here](https://dev.to/sabareh/how-to-get-the-spotify-refresh-token-176)

Save these three values in the following files:
    * .client_id
    * .client_secret
    * .refresh_token

To run the script:

    ```./spotify-playlist.py```

## Contact
Matt Dioso - dioso.matt@gmail.com

