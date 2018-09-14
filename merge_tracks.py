import appscript

iTunes = appscript.app('iTunes')
itunes_library = iTunes.library_playlists['Library']

options = {
    'go_ahead': True,
    'one': {
        'name': 'Crossfirexx',
        'artist': 'Stephen',
        # 'album': 'Sincerely',
    },
    'two': {
        'name': 'Crossfirexx',
        'artist': 'Stephen',
        'album': '',
    }
}

def search_for_track(criteria):
    i = 0
    for key, value in criteria.items():
        i += 1
        if i == 1:
            search_criteria = getattr(appscript.its, key) == value
        else:
            search_criteria = search_criteria.AND(getattr(appscript.its, key) == value)
    search_result = itunes_library.tracks[search_criteria].get()

    if len(search_result) == 0:
        raise ValueError('Track could not be found.')
        return False
    elif len(search_result) == 1:
        return search_result[0]
    elif len(search_result) > 1:
        raise ValueError('Multiple tracks found.')
        return False

track_one = search_for_track(options['one'])
track_two = search_for_track(options['two'])

track_one_date_added = getattr(track_one, 'date_added').get()
track_two_date_added = getattr(track_two, 'date_added').get()

if track_one_date_added < track_two_date_added:
    track_to_keep = track_one
    track_to_delete = track_two
else:
    track_to_keep = track_two
    track_to_delete = track_one

track_to_keep_location = getattr(track_to_keep, 'location').get()
track_to_delete_location = getattr(track_to_delete, 'location').get()

new_played_count = getattr(track_one, 'played_count').get() + getattr(track_two, 'played_count').get()
new_played_date = max(getattr(track_one, 'played_date').get(), getattr(track_two, 'played_date').get())

if options['go_ahead']:

    if track_to_keep_location == appscript.k.missing_value:
        if track_to_delete_location == appscript.k.missing_value:
            raise ValueError('Neither of the tracks have a song file location that exists.')
        else:
            getattr(track_to_keep, 'location').set(track_to_delete_location)
    getattr(track_to_keep, 'played_count').set(new_played_count)
    getattr(track_to_keep, 'played_date').set(new_played_date)

    print(
        'Keeping',
        getattr(track_to_keep, 'artist').get(),
        "-",
        getattr(track_to_keep, 'name').get(),
        "-",
        getattr(track_to_keep, 'album').get(),
    )
    print('    (because it has the oldest "date added")')
    print('    iTunes ID:', getattr(track_to_keep, 'id').get())
    print(
        'Deleted',
        getattr(track_to_delete, 'artist').get(),
        "-",
        getattr(track_to_delete, 'name').get(),
        "-",
        getattr(track_to_delete, 'album').get(),
    )
    print('    iTunes ID:', getattr(track_to_delete, 'id').get())
    print('New "played count":', new_played_count)
    print('New "played date": ', new_played_date)