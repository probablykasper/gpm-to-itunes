import appscript, json

iTunes = appscript.app('iTunes')
itunes_library = iTunes.library_playlists['Library']
md_map = json.loads(open('md_map.json').read())

tracks = itunes_library.tracks.get()
unmatched_itunes_tracks = {}
for itunes_track in tracks:
    title = getattr(itunes_track, "name").get()
    artist = getattr(itunes_track, "artist").get()
    album = getattr(itunes_track, "album").get()
    key = artist +" - "+ title +" - "+ album
    unmatched_itunes_tracks[key] = True
print(unmatched_itunes_tracks)