# gpm-to-itunes
Adds your GPM library to iTunes.

Your tracks' date added and play count will be kept. Last played date, year, album artist, composer, comment, track number, track count, genre, disc number and disc count should be kept as well.

If you have any tracks already in iTunes, they will be matched with GPM tracks so that you don't end up with duplicates. If this happens, the version in iTunes will be kept. If the iTunes track's mp3 file is missing, this will be fixed. The play counts will be combined. The "played date" that is the most recent will be used. The iTunes track's "date added" will always be used. The GPM track's year, album artist, composer, comment, track number, track count, genre, disc number, disc count, title, artist and album will be used.

In iTunes, a playlist folder named "GPM PLAYLISTS" will be created. GPM user playlists will be added into it.

GPM tracks will not keep their thumbs up or thumbs down ratings when they're added to iTunes. Instead, they will be added to two playlists that will be created, named "GPM Thumbs Up" and "GPM Thumbs Down". They will also be inside the "GPM PLAYLISTS" playlist folder.

# Guide
1. Setup
    1. Use macOS.
    1. Install Python 3 from [python.org](https://python.org).
    1. **CREATE A BACKUP OF YOUR ITUNES FOLDER** (~/Music/iTunes) in case something goes wrong.
    1. Run `python3 -m pip install gmusicapi appscript mp3_tagger tqdm` to install some stuff gpm-to-itunes needs.
    1. Create the `options.py` file. Follow the example shown below.
1. Download
    1. Run `python3 main.py login` to log in to GPM.
    1. Run `python3 main.py download`. This will download and save your GPM library's metadata to `library_downloaded.json`.
    1. Run `python3 main.py restructure`. This just does some changes to `library_downloaded.json` and saves the new version as `library_restructured.json`.
    1. Download your GPM library's songs to a folder using [Music Manager](https://play.google.com/music/listen#/manager). This can take hours. Don't move this folder anywhere before you're done with gpm-to-itunes.
1. Run `python3 main.py match_files <songs_path>`. songs_path is the path of the folder you downloaded your GPM library's songs to in the last step. This will connect the songs you downloaded and the metadata we downloaded earlier.
1. If you have tracks that exist in both iTunes and GPM



1. If you have any tracks that exist in both iTunes and GPM, but with different titles, artists or albums, you can create an `md_map.json` file, example shown below. This will make gpm-to-itunes match these songs together, so that you don't end up with duplicates.
11. If you have tracks in iTunes, run `python3 main.py scan_itunes` (Optional but recommended). This will tell you when it finds tracks that already exist in your GPM library. It will also tell you if there are duplicate tracks in iTunes (tracks with equal titles, artists and albums), which you might not want. At the end, it will tell you what tracks in iTunes don't match up with any GPM track - And it logs these in the format `md_map.json` accepts, because you might want to consider adding them there.
12. If you use `md_map.json`, run `python3 check.py` (Optional but recommended). This will tell you if there are any tracks in `md_map.json` that don't match up with any GPM track.
13. Disconnect from internet. This is because iTunes can pause step 11 by showing a popup message because we're changing the system's date and time.
14. Run `python3 add_to_itunes`. Now we actually add the tracks to iTunes. It does this by setting the system's date and time to the GPM track's "date added", then adds it to iTunes and updates it's metadata. If there are tracks that already exist in iTunes, it will
15. You can reconnect to the internet.
16. Your system's date and time might be messed up. Open the System Preferences app, go to "Date & Time" and make sure everything is good. The "Set date and time automatically" option might have been turned off and not been turned back on again.
17. Done!

# Running main.py
Run gpm-to-itunes using `python3 main.py [action] [songs_path]`.

This is gpm-to-itunes itself. Run it using `python3 main.py [action] [songs_path]`.
- `action` specifies what gpm-to-itunes will do. It be any of the following:
    - `download`: This will download and save your GPM library's metadata to `library_downloaded.json`.
    - `restructure`: This just does some changes to `library_downloaded.json` and saves the new version as `library_restructured.json`.
    - `match_files`
    - `scan_itunes`
    - `add_to_itunes`
- `songs_path` is only needed with the `match_files` action. It specifies where 
- `songs_path` is the path to the folder with your GPM songs, and you only need it when running with the `match_files` action.
If you don't provide an `action` or `songs_path`, then the `action` and `songs_path` fields from the `options.py` file will be used. This is especially useful if you want to use nodemon

# options.py
File with options for when you run main.py.
```python
options = {
    
    # Username and password for Google Play Music
    'gpm_username': '<USERNAME>',
    'gpm_password': '<PASSWORD>',

    # The default action gpm-to-itunes will do (when
    # no CLI arguments are given). These are the possible values:
    # - download
    # - restructure
    # - match_files
    # - scan_itunes
    # - add_to_itunes
    'action': 'download',

    # The default path to your downloaded GPM library songs
    'songs_path': '/Users/<USERNAME>/Downloads/mymusic',

    # Your Mac user's password. Needed for changing your computer's date and time:
    'sudo_password': '<PASSWORD>',
}
```
# md_map.json
A file that you can use to map GPM tracks to it's iTunes equivalents. Use this if you have a GPM track that already exists in iTunes, but with a different title, artist or album. Example:
```
{
    "gpm_title - gpm_artist - Surface": {
        "title": "itunes_title",
        "artist": "itunes_artist",
        "album": "itunes_album"
    },
    "Surface - Aero Chord - ": {
        "title": "Surface",
        "artist": "Aero Chord",
        "album": "Monstercat: 017 - Ascension"
    },
}
```
