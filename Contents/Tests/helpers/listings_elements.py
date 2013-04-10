endpoint = dict(
    _type = 'endpoint',
    display_title = 'foo',
    endpoint = 'bar'
)

movie = dict(
    _type = 'movie',
    display_title = 'foo',
    endpoint = 'bar'
)

movie_with_meta = movie.copy()
movie_with_meta.update(dict(
    display_overview = '42',
    artwork = 'http://example.com/artwork.jpg'
))

show = dict(
    _type = 'show',
    display_title = 'foo',
    endpoint = 'bar'
)

show_with_meta = show.copy()
show_with_meta.update(dict(
    display_overview = '42',
    artwork = 'http://example.com/artwork.jpg'
))

episode = dict(
    _type = 'episode',
    display_title = 'foo',
    endpoint = 'bar'
)

episode_with_meta = episode.copy()
episode_with_meta.update(dict(
    display_overview = '42',
    artwork = 'http://example.com/artwork.jpg'
))

foreign = dict(
    _type = 'foreign',
    domain = 'domain',
    original_url = 'original',
    foreign_url = 'foreign'
)

foreign_with_final = foreign.copy()
foreign_with_final.update(dict(
    final_url = 'final'
))

mocks = dict(
    endpoint = endpoint,
    movie = movie,
    movie_with_meta = movie_with_meta,
    show = show,
    show_with_meta = show_with_meta,
    episode = episode,
    episode_with_meta = episode_with_meta,
    foreign = foreign,
    foreign_with_final = foreign_with_final
)
