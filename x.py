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

# - Delete Child Of The Highlands (duplicate)
# - Delete Drop Tower - Firestorm (duplicate)
# - Delete Feelings by BOIRIA and ColBreakz (duplicate)
# - Delete Feelings by BOIRIA and ColBreakz (duplicate)
# - Delete Katy Perry - Roar
# - Delete Ωmega (LUMBERJVCK Remix) (duplicate)
# - Delete Au5 & heavy J - Au5 & heavy J - Dream Of Love (feat. Kenny Raye) (Vulpey Remix) (duplicate)
# - Delete Thomas Hayes ft. Joni Fatora - Neon (Ryos Remix) [T-Mass & Denis Elezi Refix] (duplicate)

# - Delete Dillon Francis, DJ Snake - Get Low
# - Delete [Glitch Hop] Electromagnetic Blaze - Telescopes
# - Delete Didrick - Monstercat Live Performance (3 Year Anniversary Mix)

# - Delete Michael Jackson - Beat It (Do It) (Remix feat. Shia LaBeouf)
# - Delete Sonic Remix MegaMix Vol. 1
# - Delete Sonic Remix MegaMix Vol. 2
# - Delete Kaspers iPhone 6 - New Recording
# - Delete Kaspers iPhone 6 - Scream

# - Delete all podcasts
