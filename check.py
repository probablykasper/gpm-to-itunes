import json
def load_library(path = "library.json"):
    print('Loading GPM library...')
    gpm_library = json.loads(open(path).read())
    print("    Track count:", len(gpm_library["tracks"]))
    print("    Playlist count:", len(gpm_library["playlists"]))
    return gpm_library

md_map = json.loads(open('md_map.json').read())
gpm_library = load_library('library_matched_files.json')


# Commented out because I think it does what main.py does when it scans itunes and outputs JSON

# import appscript
# iTunes = appscript.app('iTunes')
# itunes_library = iTunes.library_playlists['Library']
# new_md_map = {}
# for key, item in md_map.items():
#     md_map_key = item['artist'] + " - " + item['title'] + " - " + item['album']
#     # print(md_map_key)
#     new_md_map[md_map_key] = True
# tracks = itunes_library.tracks.get()
# x = {}
# print("iTunes tracks that aren't matched with a gpm track and is not in md_map.json:")
# for track in tracks:
#     name = getattr(track, 'name').get()
#     artist = getattr(track, 'artist').get()
#     album = getattr(track, 'album').get()
#     # gpm_track['md_map'] = False
#     key = artist + " - " + name + " - " + album
#     # if key in md_map:
#         # gpm_track['md_map'] = True
#         # name = md_map[key]['title']
#         # artist = md_map[key]['artist']
#         # album = md_map[key]['album']
#         # key = artist + " - " + name + " - " + album
#     if key not in gpm_library['tracks']:
#         if key not in new_md_map:
#             # x[name + " - " + artist + " - " + album] = {
#             #     "title": name,
#             #     "artist": artist,
#             #     "album": album,
#             # }
#             print(key)

print("Tracks in md_map.json that don't correspond to a gpm track:")
md_map_copy = md_map.copy()
for key, gpm_track in gpm_library['tracks'].items():
    key = gpm_track['title'] + " - " + gpm_track['artist'] + " - " + gpm_track['album']
    if key in md_map_copy:
        md_map_copy.pop(key, None)
import pprint
pprint = pprint.PrettyPrinter(indent=4).pprint
print(json.dumps(md_map_copy, indent=4))