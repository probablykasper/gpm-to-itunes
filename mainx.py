from gmusicapi import Mobileclient
import json, datetime, appscript, pprint, sys, os
pprint = pprint.PrettyPrinter(indent=4).pprint

from options import options
if len(sys.argv) > 1:
    options['action'] = sys.argv[1]
if options['action'] == 'match files' and len(sys.argv) > 2:
    options['songs_path'] = sys.argv[2]

def save_library(path, content):
    file = open(path, "w+")
    file.write(json.dumps(content, indent=2))
    file.close()

def download_library():
    api = Mobileclient()
    logged_in = api.login(options['gpm_username'], options['gpm_password'], Mobileclient.FROM_MAC_ADDRESS)
    if logged_in == False:
        sys.exit("Couldn't log in.")
    if not api.is_authenticated:
        sys.exit("Couldn't log in. Wrong credentials")
    library = {
        'tracks': api.get_all_songs(),
        'playlists': api.get_all_user_playlist_contents(),
    }
    save_library('library_downloaded.json', library)
    return library

def generate_key(track):
    # format: 'artist - title - album'
    return '%s - %s - %s' % (track['artist'], track['title'], track['album'])

def restructure_library(original_library):
    library = {
        'tracks': {},
        'playlists': original_library['playlists'],
    }
    duplicates = 0
    for gpm_track in original_library['tracks']:
        key = generate_key(gpm_track)
        if key in original_library['tracks']:
            print('   Error: Duplicate track "' + key + '"')
            duplicates += 1
        else:
            library['tracks'][key] = gpm_track
    save_library('library_restructured.json', library)
    if duplicates != 0:
        print("Found ' + str(duplicates) + ' duplicates. \
        If you proceed, only one of the duplicates will be kept. \
        To fix this, delete or rename tracks from your GPM library \
        that have the same artist name, title and album. Note that this means \
        you'll also have to re-download your music if you've already downloaded it'")

def load_library(library_path):
    print('Loading GPM library...')
    json_library = open(library_path).read()
    data = json.loads(json_library)
    print("    Track count:", len(gpm_library["tracks"]))
    print("    Playlist count:", len(gpm_library["playlists"]))
    return data

if options['action'] == 'download':
    print('Downloading GPM library...')
    gpm_library = download_library()
    print("    Track count:", len(gpm_library["tracks"]))
    print("    Playlist count:", len(gpm_library["playlists"]))
elif options['action'] == 'restructure':
    gpm_library = load_library("library_downloaded.json")
    print('Restructuring GPM library...')
    gpm_library = restructure_library(gpm_library)
elif options['action'] == 'match files':
    gpm_library = load_library()
    print('Matching GPM library with song files...')
    for subdir, dirs, files in os.walk(options['songs_path']):
        for file in files:
            file_path = os.path.join(subdir, file)
            filename, extension = os.path.splitext(file_path)
            if extension != ".mp3":
                continue
            gpm_library['']
    
else:
    sys.exit('Unknown action "'+options['action']+'"')


# loop through audio files
#     get the audio file's artist/title
#     loop through json library for a match, append the file path to the json library track
#     or maybe use the python get() thing to look for the right artist/title match
#     add iTunes metadata (plays, loved/disliked, date added/played/modified)
# loop through json library
#     set clock
#     add track to iTunes