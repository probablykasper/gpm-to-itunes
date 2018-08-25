from gmusicapi import Mobileclient
import json, datetime, appscript, pprint, sys
import conf
pprint = pprint.PrettyPrinter(indent=4).pprint

options = {
    'gpm_username': '',
    'gpm_password': '',
    'action': 'loadx',
    'songs_path': '',
}
if len(sys.argv) > 1:
    options['action'] = sys.argv[1]
if options['action'] == 'match_files' and len(sys.argv) > 2:
    options['songs_path'] = sys.argv[2]

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
    json_library = json.dumps(library, indent=2)
    open("./library_original.json", "w+").write(json_library).close()
    return library

def generate_key(track):
    # format: 'artist - title - album'
    return '%s - %s - %s' % (gpm_track['artist'], gpm_track['title'], gpm_track['album'])

def restructure_library(original_library):
    library = {
        'tracks': {},
        'playlists': {},
    }
    duplicates = 0
    for gpm_track in original_library['tracks']:
        key = generate_key(gpm_track)
        if key in original_library['tracks']:
            print('   Error: Duplicate track "' + key + '"')
            duplicates += 1
        else:
            library[key] = gpm_track
    json_library = json.dumps(library, indent=2)
    open("./library.json", "w+").write(json_library).close()
    if duplicates != 0:
        print("Found ' + str(duplicates) + ' duplicates. \
        If you proceed, only one of the duplicates will be kept. \
        To fix this, delete or rename tracks from your GPM library \
        that have the same artist name, title and album. Note that this means \
        you'll also have to re-download your music if you've already downloaded it'")

def load_library():
    json_library = open("./library.json").read()
    data = json.loads(json_library)
    return data

if options['action'] == 'download':
    print('Downloading GPM library...')
    gpm_library = download_library()
    print("    Track count:", len(gpm_library["tracks"]))
    print("    Playlist count:", len(gpm_library["playlists"]))
    print('Restructuring GPM library...')
    gpm_library = restructure_library(gpm_library)
elif options['action'] == 'match_files':
    print('Loading GPM library...')
    gpm_library = load_library()
    print("    Track count:", len(gpm_library["tracks"]))
    print("    Playlist count:", len(gpm_library["playlists"]))
    print('Matching GPM library with song files...')
    
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