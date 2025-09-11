from unittest.mock import MagicMock

import pytest
import ytmusicapi

from api.lyrics import LyricsDownloader
from api.ytmusic import LyricsResult, SearchResult, SongArtist, YTMusic


@pytest.fixture
def lyrics_downloader():
    return MagicMock(spec=LyricsDownloader)


@pytest.fixture
def ytmusic(lyrics_downloader):
    return YTMusic(lyrics_downloader)


def test_search(ytmusic: YTMusic):
    ytmusic.client.search = MagicMock(
        return_value=[
            {
                "title": "Song Title",
                "artists": [{"name": "Artist Name", "id": "artist_id"}],
                "duration": 300,
                "video_id": "video_id",
            },
        ],
    )
    results = ytmusic.search("Song Title")
    assert len(results) == 1
    assert results[0].title == "Song Title"
    assert results[0].artist[0].name == "Artist Name"
    assert results[0].duration == 300
    assert results[0].video_id == "video_id"


def test_get_formated_artist(ytmusic):
    song = SearchResult(
        title="Song Title",
        artist=[
            SongArtist(name="Artist Name", id="artist_id"),
            SongArtist(name="Artist Name 2", id="artist_id2"),
        ],
        duration=300,
        video_id="video_id",
    )
    assert song.get_formatted_artists() == "Artist Name, Artist Name 2"


def test_search_invalid_filter(ytmusic):
    with pytest.raises(TypeError):
        ytmusic.search("query", 123)


def test_search_invalid_query(ytmusic):
    with pytest.raises(TypeError):
        ytmusic.search(123)


def test_get_lyrics(ytmusic: YTMusic):
    song = SearchResult(
        title="Song Title",
        artist=[SongArtist(name="Artist Name", id="artist_id")],
        duration=300,
        video_id="video_id",
    )
    ytmusic.client.get_watch_playlist = MagicMock(return_value={"lyrics": "lyrics_id"})
    ytmusic.client.get_lyrics = MagicMock(
        return_value={"lyrics": "Lyrics text", "source": "Source"},
    )
    ytmusic.lyrics_downloader.save = MagicMock(
        return_value=LyricsResult(lyrics="Lyrics text", source="Source"),
    )

    lyrics_result: LyricsResult = ytmusic.get_lyrics(song)
    assert lyrics_result.lyrics == "Lyrics text"
    assert lyrics_result.source == "Source"


def test_get_lyrics_no_lyrics(ytmusic: YTMusic):
    song = SearchResult(
        title="Song Title",
        artist=[SongArtist(name="Artist Name", id="artist_id")],
        duration=300,
        videoId="video_id",
    )
    ytmusic.client.get_watch_playlist = MagicMock(return_value={"lyrics": "lyrics_id"})
    ytmusic.client.get_lyrics = MagicMock(
        side_effect=ytmusicapi.exceptions.YTMusicError,
    )
    ytmusic.lyrics_downloader.save = MagicMock(
        return_value=LyricsResult(lyrics="None", source="None"),
    )

    lyrics_result = ytmusic.get_lyrics(song)
    assert lyrics_result.lyrics == "None"
    assert lyrics_result.source == "None"
