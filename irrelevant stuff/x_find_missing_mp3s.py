# what this was supposed to do was to find tracks with a missing mp3 file.

import json, appscript
md_map = json.loads(open('md_map.json').read())

listOfTracks = {}
for key, track_md in md_map.items():
    key = track_md['title'] +" - "+ track_md['artist'] +" - "+ track_md['album']
    listOfTracks[key] = True


iTunes = appscript.app('iTunes')
itunes_library = iTunes.library_playlists['Library']
whoops_playlist = iTunes.playlists[appscript.its.name == '...WOOPS']

tracks = whoops_playlist.tracks[appscript.its.album != 'ahfucktoast'].get()[0]
for track in tracks:
    title = getattr(track, "name").get()
    artist = getattr(track, "artist").get()
    album = getattr(track, "album").get()
    key = artist +" - "+ title +" - "+ album
    if key in listOfTracks:
        print("exists")
    else:
        print("nope")
        print(key)