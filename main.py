from gmusicapi import Mobileclient
import json, datetime, pprint, sys, os
import appscript # pip3 install distribute; sudo distribute
from tqdm import tqdm
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
pprint = pprint.PrettyPrinter(indent=4).pprint

from options import options
if len(sys.argv) > 1:
    options['action'] = sys.argv[1]
if options['action'] == 'match_files' and len(sys.argv) > 2:
    options['songs_path'] = sys.argv[2]

def load_library(path = "library.json"):
    print('Loading GPM library...')
    gpm_library = json.loads(open(path).read())
    print("    Track count:", len(gpm_library["tracks"]))
    print("    Playlist count:", len(gpm_library["playlists"]))
    return gpm_library
def save_library(content, path = "library.json"):
    file = open(path, "w+")
    file.write(json.dumps(content, indent=2))
    file.close()

def get_key(track, id3_tags = False):
    # format: 'artist - title - album'
    if 'title' in track:
        return '%s - %s - %s' % (track.get('artist', ''), track.get('title', ''), track.get('album', ''))
    elif 'song' in track:
        return '%s - %s - %s' % (track.get('artist', ''), track.get('song', ''), (track.get('album', '') or ''))

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
    return library

def restructure_library(original_library):
    library = {
        'tracks': {},
        'playlists': original_library['playlists'],
    }
    duplicates = 0
    for gpm_track in original_library['tracks']:
        key = get_key(gpm_track)
        if key in original_library['tracks']:
            print('   Error: Duplicate track "' + key + '"')
            duplicates += 1
        else:
            library['tracks'][key] = gpm_track
    if duplicates != 0:
        print("Found ' + str(duplicates) + ' duplicates. \
        If you proceed, only one of the duplicates will be kept. \
        To fix this, delete or rename tracks from your GPM library \
        that have the same artist name, title and album. Note that this means \
        you'll also have to re-download your music if you've already downloaded it'")
    return library

def match_files(gpm_library):
    # scan how many files there are
    fileCount = 0
    for subdir, dirs, files in os.walk(options['songs_path']):
        fileCount += len(files)
    with tqdm(total=fileCount) as progressbar:
        for subdir, dirs, files in os.walk(options['songs_path']):
            for file in files:
                file_path = os.path.join(subdir, file)
                filename, extension = os.path.splitext(file_path)
                if extension != ".mp3": continue
                mp3 = MP3File(file_path)
                mp3.set_version(VERSION_2)
                key = get_key(mp3.get_tags(), True)

                gpm_track = gpm_library['tracks'][key]
                tqdm.write('    '+gpm_track['title'])
                track_md = {
                    'played_count': gpm_track['playCount'],
                    'loved': True if 'rating' in gpm_track and gpm_track['rating'] == '5' else False,
                    'disliked': True if 'rating' in gpm_track and gpm_track['rating'] == '1' else False,
                    'date_added': gpm_track['creationTimestamp'],
                    'played_date': gpm_track['recentTimestamp'],
                    'modification_date': gpm_track['lastModifiedTimestamp'],
                }
                if key in gpm_library['tracks']:
                    track_md['file_path'] = file_path
                else:
                    tqdm.write('    Error: Track "%s" could not be matched to GPM library.' % (key))
                gpm_library['tracks'][key]['track_md'] = track_md
                progressbar.update(1)
    for key, track in gpm_library['tracks'].items():
        if 'track_md' not in track:
            if 'file_path' not in track['track_md']:
                print('Error: Track "%s" could not be associated with a song file' % (key))
    return gpm_library

def add_to_itunes(gpm_library):
    import subprocess
    usingnetworktime_cmd = 'echo 123 | sudo -S systemsetup -getusingnetworktime'.split()
    usingnetworktime_output = subprocess.check_output(usingnetworktime_cmd).decode("utf-8")
    original_usingnetworktime = 'off' if 'Network Time: Off' in usingnetworktime_output else 'on'
    
    # stop using network time (so that we can edit time)
    subprocess.call(
        ('echo %s | sudo -S systemsetup -setusingnetworktime %s'
        % (options['sudo_password'], 'off')).split()
    )

    def gpm_timestamp_to_date(gpm_timestamp):
        timestamp = int(gpm_timestamp)/1e6
        date = datetime.datetime.fromtimestamp(timestamp)
        return date

    for key, gpm_track in tqdm(gpm_library['tracks'].items()):
        track_md = gpm_track['track_md']
        tqdm.write(track_md['date_added'])

        date_added = gpm_timestamp_to_date(track_md['date_added'])
        date = date_added.strftime('%m:%d:%y') # mm:dd:yy
        time = date_added.strftime('%H:%M:%S') # hh:mm:ss
        # subprocess.call(
        #     ('echo %s | sudo -S systemsetup -setdate %s -settime %s'
        #     % (options['sudo_password'], date, time)).split()
        # )
        iTunes = appscript.app('iTunes')
        # new_itunes_track = appscript.file('/Users/kasp/Downloads/mooosik/Zetta/00 Greensleeves.mp3').add()
        
        # posix_path_cmd = ['osascript', '-e', "'"+'POSIX path of POSIX file "'+track_md['file_path']+'"'+"'"]
        # posix_path_cmd = ['osascript', '-e', '\'POSIX path of POSIX file "%s"\'' % (track_md['file_path'])]
        # posix_path_cmd = 'osascript -e \'POSIX path of POSIX file "%s"\'' % (track_md['file_path'])
        posix_path_cmd = """  osascript -e 'POSIX file "%s" as string'  """ % (track_md['file_path'])
        posix_path = subprocess.check_output(posix_path_cmd, shell=True).decode("utf-8").rstrip()
        print(posix_path)
        new_itunes_track = iTunes.add(posix_path)
        print(new_itunes_track)
        import time
        time.sleep(10)
    
    # set network time to what it was before
    subprocess.call(
        ('echo %s | sudo -S systemsetup -setusingnetworktime %s'
        % (options['sudo_password'], original_usingnetworktime)).split()
    )

if options['action'] == 'download':
    print('Downloading GPM library...')
    gpm_library = download_library()
    save_library(gpm_library, 'library_downloaded.json')
    print("    Track count:", len(gpm_library["tracks"]))
    print("    Playlist count:", len(gpm_library["playlists"]))
elif options['action'] == 'restructure':
    gpm_library = load_library("library_downloaded.json")
    print('Restructuring GPM library...')
    gpm_library = restructure_library(gpm_library)
    save_library(gpm_library, 'library_restructured.json')
elif options['action'] == 'match_files':
    gpm_library = load_library('library_restructured.json')
    print('Matching GPM library with song files...')
    gpm_library = match_files(gpm_library)
    save_library(gpm_library, 'library_matched_files.json')
elif options['action'] == 'add_to_itunes':
    gpm_library = load_library('library_matched_files.json')
    print('Setting system clock, adding tracks to iTunes and updating metadata...')
    add_to_itunes(gpm_library)
# elif add_to_itunes
    # set clock
    # add track to iTunes
    # get the iTunes track, and update it's metadata
    
else:
    sys.exit('Unknown action "'+options['action']+'"')

# loop through audio files
#     -get the audio file's artist/title
#     -loop through json library for a match, append the file path to the json library track
#     -or maybe use the python get() thing to look for the right artist/title match
#     add iTunes metadata (plays, loved/disliked, date added/played/modified)
# loop through json library
#     set clock
#     add track to iTunes