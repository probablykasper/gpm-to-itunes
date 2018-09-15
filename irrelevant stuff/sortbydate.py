import json, datetime

def load_library(path = "library.json"):
    print('Loading GPM library...')
    gpm_library = json.loads(open(path).read())
    print("    Track count:", len(gpm_library["tracks"]))
    print("    Playlist count:", len(gpm_library["playlists"]))
    return gpm_library
def save_library(content, path):
    file = open(path, "w+")
    file.write(json.dumps(content, indent=2))
    file.close()

def gpm_timestamp_to_date(gpm_timestamp):
    timestamp = int(gpm_timestamp)/1e6
    date = datetime.datetime.fromtimestamp(timestamp)
    return date

gpm_library = load_library('library_matched_files.json')
new_library = []
for key, track in gpm_library['tracks'].items():
    new_library.append({
        'track_key': key,
        'gpmdate': track['creationTimestamp'],
        'date': gpm_timestamp_to_date(track['creationTimestamp']).strftime('%B %d %Y'),
    })

from operator import itemgetter
newlist = sorted(new_library, key=itemgetter('gpmdate'))

save_library(newlist, 'libsortedbydate.json')