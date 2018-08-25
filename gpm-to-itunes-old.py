from gmusicapi import Mobileclient
import datetime
import pprint
import json
import appscript
pprint = pprint.PrettyPrinter(indent=4).pprint

options = {
    "gpmUsername": "",
    "gpmPassword": "",
    "useOffline": True,
    "ignoreUnmatched": False,
}

iTunes = appscript.app('iTunes')

def get_online_library():
    api = Mobileclient()
    logged_in = api.login("kasperkh.kh@gmail.com", "yesilly12twat", Mobileclient.FROM_MAC_ADDRESS)
    if logged_in == False:
        sys.exit("Couldn't log in.")
    if not api.is_authenticated:
        sys.exit("Couldn't log in. Wrong credentials")

    library = {
        "tracks": api.get_all_songs(),
        "playlists": api.get_all_user_playlist_contents(),
    }
    return library

def write_library_file(library):
    file = open("./library.json", "w+")
    json_library = json.dumps(library, indent=2)
    file.write(json_library)
    file.close()

def get_offline_library():
    json_library = open("./library.json").read()
    data = json.loads(json_library)
    return data

def get_and_write_library():
    write_library_file(get_online_library())

def matchTracks(gpmLibrary, iTunesLibrary):
    duplicateTracks = 0
    unmatchedTracks = 0
    for gpmTrack in gpmLibrary["tracks"]:
        searchCriteria = appscript.its.name == gpmTrack["title"]
        searchCriteria = searchCriteria.AND(
            appscript.its.artist == gpmTrack["artist"])
        searchResult = iTunesLibrary.tracks[searchCriteria].get()
        if len(searchResult) == 1:
            iTunesTrack = searchResult[0]
        elif len(searchResult) == 0:
            iTunesTrack = 0
            duplicateTracks += 1
            print("    Found "+len(iTunesTrack)-1+"duplicate(s) of track: " + gpmTrack["artist"]+" - "+gpmTrack["title"])
        else:
            unmatchedTracks += 1
            iTunesTrack = 0
            print("    Could not match track: " + gpmTrack["artist"]+" - "+gpmTrack["title"])
        gpmTrack['iTunesTrack'] = iTunesTrack
    return {
        'duplicateTracks': duplicateTracks,
        'unmatchedTracks': unmatchedTracks,
    }

def gpmTimestampToAppleScriptDate(gpmTimestamp):
    timestamp = int(gpmTimestamp)/1e6
    date = datetime.datetime.fromtimestamp(timestamp)
    # Saturday, 24 March 2018 at 12:00:00 AM
    return date.strftime('%A, %d %B %Y at %I:%M:%S %p')

# print(gpmTimestampToAppleScriptDate("1451341005426614"))

def updateTracks(gpmLibrary):
    for gpmTrack in gpmLibrary["tracks"]:
        iTunesTrack = gpmTrack['iTunesTrack']
        playCount = gpmTrack['playCount']  # played_count
        rating = gpmTrack['rating'] # loved, disliked
        # creationTimestamp = int(gpmTrack['creationTimestamp'])/1e6 # date_added
        # recentTimestamp = int(gpmTrack['recentTimestamp'])/1e6 # played_date
        # lastModifiedTimestamp = int(gpmTrack['lastModifiedTimestamp'])/1e6 # modification_date
        # creationDatetime = datetime.fromtimestamp(creationTimestamp) # date_added
        # recentDatetime = datetime.fromtimestamp(recentTimestamp) # played_date
        # lastModifiedDatetime = datetime.fromtimestamp(lastModifiedTimestamp) # modification_date

        creationDatetime = gpmTimestampToAppleScriptDate(gpmTrack['creationTimestamp']) # date_added
        recentDatetime = gpmTimestampToAppleScriptDate(gpmTrack['recentTimestamp']) # played_date
        lastModifiedDatetime = gpmTimestampToAppleScriptDate(gpmTrack['lastModifiedTimestamp']) # modification_date

        # pprint(getattr(iTunesTrack, 'name').get())
        pprint(getattr(iTunesTrack, 'played_count').set(playCount))
        if rating == '5':
            pprint(getattr(iTunesTrack, 'loved').set(True))
        elif rating == '1':
            pprint(getattr(iTunesTrack, 'disliked').set(True))
        pprint(getattr(iTunesTrack, 'date_added').set(creationDatetime))
        pprint(getattr(iTunesTrack, 'played_date').set(recentDatetime))
        pprint(getattr(iTunesTrack, 'modification_date').set(lastModifiedDatetime))

def addPlaylists(gpmLibrary):
    for gpmPlaylist in gpmLibrary['playlists']:
        name = gpmPlaylist['name']
        description = gpmPlaylist['description']

        iTunesPlaylist = iTunes.make(
            new=appscript.k.playlist,
            with_properties={
                appscript.k.name: name,
                appscript.k.description: description,
            }
        )

        for gpmTrack in gpmLibrary['tracks']:
            iTunesTrack = gpmTrack['iTunesTrack']
            iTunesTrack.duplicate(
                to=iTunesPlaylist
            )

def transferLibrary():

    if not options['useOffline']:
        print('Downloading GPM library...')
        gpmLibrary = get_online_library()
        print("    Track count:", len(gpmLibrary["tracks"]))
        print("    Playlist count:", len(gpmLibrary["playlists"]))
        print('Saving library to file...')
        write_library_file(gpmLibrary)
    
    print('Loading GPM library...')
    gpmLibrary = get_offline_library()

    print("Matching Google Play Music tracks to iTunes tracks...")
    matchedTracks = matchTracks(gpmLibrary, iTunes.library_playlists['Library'])

    if matchedTracks['duplicateTracks'] != 0:
        print("    Error: There were duplicates found (Songs with both the same title and artist).")
        return
    if matchedTracks['unmatchedTracks'] != 0:
        print("    Error: {} tracks were not found.".format(matchedTracks['unmatchedTracks']))
        return
    if matchedTracks['unmatchedTracks'] == 0:
        print("    All tracks successfully matched.")

    print("Updating metadata of the matched iTunes tracks...")
    updateTracks(gpmLibrary)

    print("Adding playlists...")
    addPlaylists(gpmLibrary)

# transferLibrary()

iTunesLibrary = iTunes.library_playlists['Library']
iTunesTrack = iTunesLibrary.tracks[appscript.its.name == 'get lemon'].get()[0]
datttte = datetime.time(19, 0, 0)
pprint(getattr(iTunesTrack, 'date_added').set(
    to=datttte.strftime('%A, %d %B %Y at %I:%M:%S %p')
))
# iTunesTrack.date_added.set(datttte.strftime('%A, %d %B %Y at %I:%M:%S %p'))
# x = iTunesTrack.date_added.get()
# pprint(x)
# iTunesTrack.date_added.set(appscript.k.date=x)
# x = iTunesTrack.date_added.set('Thursday, 1 April 1976')
# pprint(getattr(iTunesTrack, 'date_added').get())


# pprint(datetime.fromtimestamp(1451340980325370/1e6))



from subprocess import Popen, PIPE
script = 'tell app "iTunes" to display dialog "Hello World"'
p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
stdout, stderr = p.communicate(script)





# tell application "iTunes"
# 	set theTrack to item 1 of (get tracks where name is "get lemon" and artist is "disciple")
	
# 	tell theTrack
# 		#set name to "Thursday, 1 April 1976 at 10:00:00 AM"
# 		set date added to "Thursday, 1 April 1976 at 10:00:00 AM"
# 	end tell
# end tell