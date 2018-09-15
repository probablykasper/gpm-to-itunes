from gmusicapi import Mobileclient
import json, datetime, pprint, sys, os, subprocess
import appscript # pip3 install distribute; sudo distribute
from tqdm import tqdm
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
pprint = pprint.PrettyPrinter(indent=4).pprint

from options import options
if len(sys.argv) > 1:
    options['action'] = sys.argv[1]
if options['action'] == 'match_files':
    if len(sys.argv) > 2:
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

def gpm_timestamp_to_date(gpm_timestamp):
    timestamp = int(gpm_timestamp)/1e6
    date = datetime.datetime.fromtimestamp(timestamp)
    return date


def get_posix_path(file_path):
    from shlex import quote
    escaped_file_path = quote(file_path).strip("'")
    posix_path_cmd = """  osascript -e 'POSIX file "%s" as string'  """ % (escaped_file_path)
    posix_path = subprocess.check_output(posix_path_cmd, shell=True).decode("utf-8").rstrip()
    return posix_path

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
        'track_keys': {},
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
            library['track_keys'][gpm_track['id']] = key
    if duplicates != 0:
        print(
            "Found ", str(duplicates), " duplicates."
            " If you proceed, only one of the duplicates will be kept."
            " To fix this, delete or rename tracks from your GPM library"
            " that have the same artist name, title and album. Note that this means"
            " you'll also have to re-download your music if you've already downloaded it"
        )
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
                track_md = {
                    'played_count': gpm_track['playCount'],
                    'loved': True if 'rating' in gpm_track and gpm_track['rating'] == '5' else False,
                    'disliked': True if 'rating' in gpm_track and gpm_track['rating'] == '1' else False,
                    'date_added': gpm_track['creationTimestamp'],
                    'played_date': gpm_track['recentTimestamp'],
                    'year': gpm_track['year'],
                    'album_artist': gpm_track['albumArtist'],
                    'composer': gpm_track['composer'],
                    'comment': gpm_track['comment'] if "comment" in gpm_track else "",
                    'track_number': gpm_track['trackNumber'],
                    'track_count': gpm_track['totalTrackCount'],
                    'genre': gpm_track['genre'],
                    'disc_number': gpm_track['discNumber'],
                    'disc_count': gpm_track['totalDiscCount'],
                }
                track_md['file_path'] = file_path
                if key in gpm_library['tracks']:
                    gpm_library['tracks'][key]['track_md'] = track_md
                else:
                    tqdm.write('    Error: Track "%s" could not be matched to GPM library.' % (key))
                progressbar.update(1)
    for key, track in gpm_library['tracks'].items():
        if 'track_md' not in track:
            if 'file_path' not in track['track_md']:
                print('Error: Track "%s" could not be associated with a song file' % (key))
    return gpm_library

def add_to_itunes(gpm_library, only_scan):
    
    iTunes = appscript.app('iTunes')
    itunes_library = iTunes.library_playlists['Library']
    md_map = json.loads(open('md_map.json').read())

    # find unmatched itunes tracks
    itunes_tracks = itunes_library.tracks.get()
    unmatched_itunes_tracks = {}
    for itunes_track in itunes_tracks:
        title = getattr(itunes_track, "name").get()
        artist = getattr(itunes_track, "artist").get()
        album = getattr(itunes_track, "album").get()
        key = title +" - "+ artist +" - "+ album
        unmatched_itunes_tracks[key] = {
            "title": title,
            "artist": artist,
            "album": album,
        }

    # scan itunes
    if True:
        print('Scanning iTunes library for already existing and duplicate tracks...')
        already_existing = 0
        duplicates = 0
        for key, gpm_track in tqdm(gpm_library['tracks'].items()):
            title = gpm_track['title']
            artist = gpm_track['artist']
            album = gpm_track['album']
            gpm_track['md_map'] = False
            md_map_key = title+" - "+artist+" - "+album
            if md_map_key in md_map:
                gpm_track['md_map'] = True
                title = md_map[md_map_key]['title']
                artist = md_map[md_map_key]['artist']
                album = md_map[md_map_key]['album']
            search_criteria = appscript.its.name == title
            search_criteria = search_criteria.AND(appscript.its.artist == artist)
            search_criteria = search_criteria.AND(appscript.its.album == album)
            search_result = itunes_library.tracks[search_criteria].get()
            if len(search_result) == 0:
                gpm_track['already_exists'] = False
            else:
                gpm_track['already_exists'] = True
                gpm_track['itunes_track'] = search_result[0]
                unmatched_itunes_tracks.pop(title+" - "+artist+" - "+album, None)
                if len(search_result) == 1:
                    tqdm.write('    Track already exists in iTunes library "%s"' % key)
                    already_existing += 1
                else:
                    tqdm.write('    Error: Duplicate(s) in iTunes library of track "%s' % key)
                    duplicates += 1
        if already_existing != 0:
            print(
                "Found", str(already_existing), "already existing track(s) in the itunes library."
                " If you proceed, the script will use the track already in iTunes."
                " The track will keep the itunes track's 'date added',"
                " use the newst 'last played date'"
                " and combine the play counts from both tracks."
            )
        if duplicates != 0:
            print(
                'Error: Found', str(duplicates), 'duplicate track(s) in the itunes library.'
                ' If you proceed, one of the duplicates will be considered an already existing track.'
            )
        print()
        print()
        print()
        for key, value in unmatched_itunes_tracks.items():
            print(key)
        print("Unmatched iTunes tracks:")
        print(json.dumps(unmatched_itunes_tracks, indent=4))

    # add tracks to itunes
    if only_scan == False:
        print('Setting system clock, adding tracks to iTunes and updating metadata...')

        # stop using network time (so that we can edit time)
        usingnetworktime_cmd = 'echo 123 | sudo -S systemsetup -getusingnetworktime'.split()
        usingnetworktime_output = subprocess.check_output(usingnetworktime_cmd).decode("utf-8")
        original_usingnetworktime = 'off' if 'Network Time: Off' in usingnetworktime_output else 'on'
        subprocess.call(
            ('echo %s | sudo -S systemsetup -setusingnetworktime %s'
            % (options['sudo_password'], 'off')), shell=True, stdout=subprocess.PIPE
        )
        print()

        # folder playlist
        itunes_folder_playlist = iTunes.make(
            new=appscript.k.folder_playlist,
            with_properties={
                appscript.k.name: 'GPM PLAYLISTS',
                appscript.k.description: 'Playlists imported from GPM using the gpm-to-itunes script',
            }
        )
        # make playlists for tracks that were liked/disliked in GPM
        thumbs_up_playlist = iTunes.make(
            new=appscript.k.user_playlist,
            with_properties={
                appscript.k.name: 'GPM Thumbs Up'
            }
        )
        thumbs_down_playlist = iTunes.make(
            new=appscript.k.user_playlist,
            with_properties={
                appscript.k.name: 'GPM Thumbs Down'
            }
        )
        # add thumbs up/down playlists to folder playlist
        thumbs_up_playlist.move(to=itunes_folder_playlist)
        thumbs_down_playlist.move(to=itunes_folder_playlist)

        FNULL = open(os.devnull, 'w')
        i = 0
        for key, gpm_track in gpm_library['tracks'].items():
            i += 1
            # if i < 6900: continue
            print(i, "       ", key)
            track_md = gpm_track['track_md']
            # tqdm.write(track_md['date_added'])

            date_added = gpm_timestamp_to_date(track_md['date_added'])
            date = date_added.strftime('%m:%d:%y') # mm:dd:yy
            time = date_added.strftime('%H:%M:%S') # hh:mm:ss
            subprocess.call(
                ('echo "%s" | sudo -S systemsetup -setdate %s -settime %s'
                % (options['sudo_password'], date, time)), shell=True, stdout=FNULL, stderr=subprocess.STDOUT
            )
            
            # add to itunes and update metadata
            gpm_track_md = gpm_track['track_md']
            if gpm_track['already_exists'] == True: # track already exists in itunes
                itunes_track = gpm_track['itunes_track']

                itunes_track_location = getattr(itunes_track, 'location').get()
                if itunes_track_location == appscript.k.missing_value:
                    import shutil, ntpath
                    filename = ntpath.basename(track_md['file_path'])
                    new_itunes_track_location = os.path.join(options['itunes_media_folder'], filename)
                    shutil.copyfile(track_md['file_path'], new_itunes_track_location)
                    new_posix_path = get_posix_path(new_itunes_track_location)
                    getattr(itunes_track, 'location').set(new_posix_path)

                itunes_played_count = getattr(itunes_track, 'played_count').get()
                gpm_played_count = gpm_track_md['played_count']
                new_played_count = itunes_played_count + gpm_played_count
                getattr(itunes_track, 'played_count').set(new_played_count)

                itunes_played_date = getattr(itunes_track, 'played_date').get()
                gpm_played_date = gpm_timestamp_to_date(gpm_track_md['played_date'])
                if itunes_played_date != appscript.k.missing_value and itunes_played_date > gpm_played_date:
                    new_played_date = itunes_played_date
                else:
                    new_played_date = gpm_played_date
                getattr(itunes_track, 'played_date').set(new_played_date)

                getattr(itunes_track, 'year').set(gpm_track_md['year'])
                getattr(itunes_track, 'album_artist').set(gpm_track_md['album_artist'])
                getattr(itunes_track, 'composer').set(gpm_track_md['composer'])
                if gpm_track["comment"] != "":
                    getattr(itunes_track, 'comment').set(gpm_track_md['comment'])
                getattr(itunes_track, 'track_number').set(gpm_track_md['track_number'])
                getattr(itunes_track, 'track_count').set(gpm_track_md['track_count'])
                getattr(itunes_track, 'genre').set(gpm_track_md['genre'])
                getattr(itunes_track, 'disc_number').set(gpm_track_md['disc_number'])
                getattr(itunes_track, 'disc_count').set(gpm_track_md['disc_count'])

                if gpm_track['md_map']:
                    getattr(itunes_track, 'name').set(gpm_track['title'])
                    getattr(itunes_track, 'artist').set(gpm_track['artist'])
                    getattr(itunes_track, 'album').set(gpm_track['album'])
            else: # track doesn't exist in itunes
                posix_path = get_posix_path(track_md['file_path'])
                gpm_track['itunes_track'] = iTunes.add(posix_path)
                itunes_track = gpm_track['itunes_track']

                getattr(itunes_track, 'played_count').set(gpm_track_md['played_count'])
                getattr(itunes_track, 'played_date').set(gpm_timestamp_to_date(gpm_track_md['played_date']))
            
            gpm_loved = gpm_track_md['loved']
            gpm_disliked = gpm_track_md['disliked']
            if (gpm_loved):
                itunes_track.duplicate(to=thumbs_up_playlist)
            elif (gpm_disliked):
                itunes_track.duplicate(to=thumbs_down_playlist)
        
        # set network time to what it was before
        subprocess.call(
            ('echo %s | sudo -S systemsetup -setusingnetworktime %s'
            % (options['sudo_password'], original_usingnetworktime)).split()
        )

    # add playlists to itunes
    if only_scan == False:
        print('Adding playlists to iTunes...')
        for gpm_playlist in gpm_library['playlists']:
            # make playlist
            if 'description' in gpm_playlist: description = gpm_playlist['description']
            else: description = ''
            itunes_playlist = iTunes.make(
                new=appscript.k.user_playlist,
                with_properties={
                    appscript.k.name: gpm_playlist['name'],
                    appscript.k.description: description,
                }
            )
            itunes_playlist.move(to=itunes_folder_playlist)
            # add songs to playlist
            for gpm_playlist_track in gpm_playlist['tracks']:
                key = gpm_library['track_keys'][gpm_playlist_track['trackId']]
                gpm_library['tracks'][key]['itunes_track'].duplicate(to=itunes_playlist)
    if only_scan == False:
        print('All done. Now make sure your clock is correct.')

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
elif options['action'] == 'scan_itunes':
    gpm_library = load_library('library_matched_files.json')
    add_to_itunes(gpm_library, only_scan=True)
elif options['action'] == 'add_to_itunes':
    gpm_library = load_library('library_matched_files.json')
    add_to_itunes(gpm_library, only_scan=False)
    
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