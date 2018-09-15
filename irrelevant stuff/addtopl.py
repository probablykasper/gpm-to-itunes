import json, appscript, random
def load_library(path = "library.json"):
    print('Loading GPM library...')
    gpm_library = json.loads(open(path).read())
    print("    Track count:", len(gpm_library["tracks"]))
    print("    Playlist count:", len(gpm_library["playlists"]))
    return gpm_library
gpm_library = load_library("library_matched_files.json")

iTunes = appscript.app('iTunes')
itunes_library = iTunes.library_playlists['Library']

pl = iTunes.make(
    new=appscript.k.user_playlist,
    with_properties={
        appscript.k.name: 'python '+str(random.randint(10000,99999))
    }
)

# gpm_track = gpm_library['tracks'].items()[5094]
# key = gpm_library['tracks'].keys()[5094]

# print(key)

# search_criteria = appscript.its.name == gpm_track['title']
# search_criteria = search_criteria.AND(appscript.its.artist == gpm_track['artist'])
# search_criteria = search_criteria.AND(appscript.its.album == gpm_track['album'])
# search_result = itunes_library.tracks[search_criteria].get()
search_result = itunes_library.tracks[appscript.its.name == "We Won't Be Alone (feat. Laura Brehm)"].get()
pl = iTunes.playlists[appscript.its.name == "xvx"].get()

itunes_track = search_result[0]
itunes_track_location = getattr(itunes_track, 'location').get()
if itunes_track_location == appscript.k.missing_value:
    print("yupyap")

# itunes_track.duplicate(to=pl)