from seinfeld.get_data import load_episodes

NOT_GONNA_PARSE = (
    "https://www.seinfeldscripts.com/TheSuzie.htm",
    "https://www.seinfeldscripts.com/TheChineseWoman.htm",
    "https://www.seinfeldscripts.com/ThePackage.htm",
    "https://www.seinfeldscripts.com/TheOpposite.htm",
    "https://www.seinfeldscripts.com/TheStall.htm",
    "https://www.seinfeldscripts.com/TheParkingGarage.htm",
    "https://www.seinfeldscripts.com/TheEngagement.html",
    "https://www.seinfeldscripts.com/TheBris.htm",
    "https://www.seinfeldscripts.com/TheLimo.html"
)

df = load_episodes("data.pq")

# filter out stuff we can't parse :( maybe one day
df = df[~df["url"].isin(NOT_GONNA_PARSE)]



"""
OUTLINE

intro:
    basic summary stats:
        who says the most overall
            by episode over time
            by season over time
            by character over time
            most common words for each character (exclude stopwords)

    intermediate summary stats:
        clustering:
            each line as a doc (by actor, season, episode, ...)

methods of happiness/sadness/valence like why would we do this also some like clear jokes and quotes:
    how we got the data
    how we got the lookup data and like how it was collected
    how we threw out a few episodes because we are lazy :(

    time series of valence:
        happiness over time:
            per character
            overall

    slang??:

    real world events that happened during air??:


nerdy shit:
    allotax plots:
        explain allotax
        character vs rest of the show
        least happy episode vs happiest episode ect
    shifterator:
        explain shifterator
        character vs character
        season vs season
        least happy episode vs happiest episode ect

outro:
    conclusion/end
    what would be cool in next steps with more time and data/annotations

references
    ...
"""
