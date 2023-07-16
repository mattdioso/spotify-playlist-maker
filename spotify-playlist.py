#!/usr/bin/env python3
import requests
import os
import json
import base64
import datetime

def get_client_id():
  f_id = open(".client_id", "r")
  client_id = f_id.readline().replace("\n", "")
  f_id.close()
  return client_id

def get_client_secret():
  f_secret = open(".client_secret", "r")
  client_secret = f_secret.readline().replace("\n", "")
  f_secret.close()
  return client_secret

def get_refresh_token():
  f_refresh = open(".refresh_token", "r")
  refresh_token = f_refresh.readline().replace("\n", "")
  f_refresh.close()
  return refresh_token

def get_access_token():
  f_access = open(".access_token", "r")
  access_token = f_access.readline().replace("\n", "")
  f_access.close()
  return access_token

def write_access_token(access_token):
  f_access = open(".access_token", "w")
  f_access.write(access_token)
  f_access.close()

def testConnection(access_token):
  url = "https://api.spotify.com/v1/me"
  headers = {
    'Authorization': 'Bearer ' + access_token
  }
  response = requests.get(url, headers=headers)
  return response

def get_new_access_token(refresh_token, client_id, client_secret):
  url = "https://accounts.spotify.com/api/token"
  payload = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
  }
  auth_string = client_id + ":" + client_secret
  encoded_bytes = base64.b64encode(auth_string.encode("utf-8"))
  encoded_str = str(encoded_bytes, "utf-8")
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ' + encoded_str
  }

  response = requests.post(url, headers=headers, data=payload)
  access_token = response.json()['access_token']
  write_access_token(access_token)
  return access_token

def search_for_playlist(playlist_name, access_token):
  url = "https://api.spotify.com/v1/me/playlists?limit=<LIMIT>&offset=<OFFSET>"
  headers = {
    'Authorization': 'Bearer ' + access_token
  }
  page = 0
  limit = 20
  total = 10000
  while (page*limit) + limit < total:
    offset = page * 20
    response = requests.get(url.replace("<LIMIT>", str(limit)).replace("<OFFSET>", str(offset)), headers=headers)
    for item in response.json()['items']:
      if item['name'] == playlist_name:
        return item['id']
    total = response.json()['total']
    page += 1
  print("made it out without findinig the playlist")
  return ""

def get_recent_top_tracks(access_token):
  url = "https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=<LIMIT>&offset=<OFFSET>"
  headers = {
    'Authorization': 'Bearer ' + access_token
  }
  page = 0
  limit = 20
  total = 10000
  top_tracks = []
  while (page * limit)  < total:
    offset = page * limit
    response = requests.get(url.replace("<LIMIT>", str(limit)).replace("<OFFSET>", str(offset)), headers=headers)
    for item in response.json()['items']:
      top_tracks.append(item['id'] + "\t" + item['name'])
    total = response.json()['total']
    page += 1
  return top_tracks

def get_my_user_id(access_token):
  url = "https://api.spotify.com/v1/me"
  headers = {
    'Authorization': 'Bearer ' + access_token
  }
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    return response.json()['id']
  else:
    return ""

def create_playlist(access_token, user_id, playlist_name):
  url = "https://api.spotify.com/v1/users/<USER>/playlists"
  data = {
    'name': playlist_name,
    'description': 'This playlist was created by some software i wrote',
    'public': True
  }

  headers = {
    'Authorization' : 'Bearer ' + access_token,
    'Content-Type': 'application/json'
  }

  response = requests.post(url.replace("<USER>", user_id), headers=headers, data=json.dumps(data))
  if response.status_code == 201:
    return response.json()['id']
  else:
    return ""

def get_playlist_tracks(access_token, playlist_id):
  url = "https://api.spotify.com/v1/playlists/<ID>/tracks"
  headers = {
    'Authorization': 'Bearer ' + access_token
  }

  response = requests.get(url.replace("<ID>", playlist_id), headers=headers)
  if response.status_code >= 200 and response.status_code < 300:
    return response.json()['items']
  else:
    return []

def filter_top_tracks(existing_tracks, top_tracks):
  filtered_tracks = []
  for item in top_tracks:
    filtered = filter(lambda track: track['track']['id'] == item.split("\t")[0], existing_tracks)
    if len(list(filtered)) == 0:
      filtered_tracks.append("spotify:track:" + item.split("\t")[0])
      print("adding " + str(item.split("\t")[1]))
  return filtered_tracks

def update_playlist(playlist_id, tracks, access_token):
  url = "https://api.spotify.com/v1/playlists/<PLAYLIST>/tracks"
  headers = {
    'Authorization': 'Bearer ' + access_token
  }

  data = {
    'uris': tracks
  }

  response = requests.post(url.replace("<PLAYLIST>", playlist_id), headers=headers,data=json.dumps(data))
  if response.status_code == 200:
    return response.json()['snapshot_id']
  else:
    return ""

client_id = get_client_id()
client_secret = get_client_secret()
refresh_token = get_refresh_token()
access_token = get_access_token()

auth_string = client_id.replace("\n", "") + ":" + client_secret.replace("\n", "")

encoded_bytes = base64.b64encode(auth_string.encode("utf-8"))
encoded_str = str(encoded_bytes, "utf-8")

headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Authorization': 'Basic ' + encoded_str
}

payload= {
  "grant_type": "client_credentials"
}

url = 'https://accounts.spotify.com/api/token'
response = testConnection(access_token)

if response.status_code in [401, 403]:
  print("time to re-up")
  access_token = get_new_access_token(refresh_token, client_id, client_secret)

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
year = date.strftime("%Y")
month = date.strftime("%B")
print(str.lower(month) + " " + year)
playlist_name = str.lower(month) + " " + year
playlist_id = search_for_playlist(playlist_name, access_token)
if not playlist_id:
  print("playlist_id empty")
  user_id = get_my_user_id(access_token)
  playlist_id = create_playlist(access_token, user_id, playlist_name)
  print(playlist_id)
else:
  print(playlist_id)

top_tracks = get_recent_top_tracks(access_token)
existing_tracks = get_playlist_tracks(access_token, playlist_id)
deltas = filter_top_tracks(existing_tracks, top_tracks)
if not deltas:
  print("nothing to update today")
else:
  snapshot_id = update_playlist(playlist_id, deltas, access_token)
  print(snapshot_id)
print("done")
