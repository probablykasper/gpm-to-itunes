# gpm-to-itunes
Adds your GPM library to iTunes.

Your tracks' date added and play counts will be kept, as well as last played date, year, album artist, composer, comment, track number, track count, genre, disc number and disc count is kept as well.

If you have any tracks already in iTunes, they will be matched with GPM tracks so that you don't end up with duplicates. If this happens:
- The iTunes file and "date added" will be kept
- The play counts will be combined
- The most recent "played date" will be used
- The GPM track's year, album artist, composer, comment, track number, track count, genre, disc number, disc count, title, artist and album will be used.

In iTunes, a playlist folder named "GPM PLAYLISTS" will be created. GPM user playlists will be added into it.

GPM tracks will not keep their thumbs up or thumbs down ratings when they're added to iTunes. Instead, they will be added to two playlists that will be created, named "GPM Thumbs Up" and "GPM Thumbs Down". They will be put inside the "GPM PLAYLISTS" playlist folder.

# Guide
1. Setup
    1. Use macOS.
    1. Install Python 3 from [python.org](https://python.org).
    1. **CREATE A BACKUP OF YOUR ITUNES FOLDER** (~/Music/iTunes) in case something goes wrong.
    1. Run `python3 -m pip install gmusicapi appscript mp3_tagger tqdm` to install some stuff gpm-to-itunes needs.
    1. Create the `options.py` file. Follow the example shown below.
1. Download
    1. Run `python3 main.py login` to log in to GPM. Instructions will be shown.
    1. Run `python3 main.py fetch`. This downloads metadata from GPM and restructures it.
    1. Download your GPM library's songs to a folder using [Music Manager](https://play.google.com/music/listen#/manager). This can take hours. Don't move this folder anywhere before you're done with gpm-to-itunes.
1. Preparations
    1. Run `python3 main.py match_files <songs_path>`. Replace `songs_path` with the path of the folder you downloaded your GPM library's song files into. This command will connect the files to the metadata.
    1. If you have tracks that exist in both iTunes and GPM, but have different titles, artists and/or albums, you can create an `md_map.json` file, which will make gpm-to-itunes match those songs together, so you won't end up with duplicates. If you think you may have made some mistakes, running `python3 check_md_map.py` can help spot some of them.
    1. If you have tracks in iTunes, run `python3 main.py scan_itunes` (Optional but recommended). It will tell you:
        - When it finds tracks that already exist in your GPM library.
        - When it finds duplicate tracks in iTunes (tracks with equal titles, artists and albums). If there are, a GPM track would match one of them randomly.
        - When tracks in iTunes don't match up with any GPM track. To make these easier to add to `md_map.json`, they are logged in the format the file uses.
1. Importing to iTunes
    1. Disconnect from internet. We'll be changing the system's date and time to preserve the "date added", and this causes iTunes to show popups that pause gpm-to-itunes.
    1. Run `python3 add_to_itunes` to add the tracks to iTunes. It will set the system's date and time to preserve the "date added", then adds it to iTunes and updates it's metadata.
    1. Reconnect to the internet.
    1. Open "Date & Time" in the System Preferences app, and make sure the date and time is right, and that the "Set date and time automatically" option is what you prefer (It's usually on).
    1. Done!

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

# user_files/md_map.json
A file that you can use to map GPM tracks to it's iTunes equivalents. Use this if you have a GPM track that already exists in iTunes, but with a different title, artist or album. Example:
```
{
    "gpm_title - gpm_artist - gpm_album": {
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
