endpoint = dict(
    _type         = 'endpoint',
    display_title = 'foo',
    endpoint      = 'bar'
)

movie = dict(
    _type            = 'movie',
    display_title    = 'foo',
    endpoint         = 'bar',
    display_overview = '42',
    artwork          = 'http://example.com/artwork.jpg'
)

show = dict(
    _type            = 'show',
    display_title    = 'foo',
    endpoint         = 'bar',
    display_overview = '42',
    artwork          = 'http://example.com/artwork.jpg'
)

episode = dict(
    _type            = 'episode',
    display_title    = 'foo 1x1 episode title',
    endpoint         = '/shows/1/episode/1',
    display_overview = '42',
    artwork          = 'http://example.com/artwork.jpg'
)

episode2 = dict(
    _type            = 'episode',
    display_title    = 'foo: episode title 01.01.2013',
    endpoint         = '/shows/1/episode/2',
    display_overview = '42',
    artwork          = 'http://example.com/artwork.jpg'
)

foreign = dict(
    _type        = 'foreign',
    domain       = 'domain',
    original_url = 'original',
    foreign_url  = 'foreign'
)

foreign_with_final = foreign.copy()
foreign_with_final.update(dict(
    final_url = 'final'
))

mocks = dict(
    endpoint           = endpoint,
    movie              = movie,
    show               = show,
    episode            = episode,
    episode2           = episode2,
    foreign            = foreign,
    foreign_with_final = foreign_with_final
)
