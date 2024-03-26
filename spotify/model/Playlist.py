from typing import List
from typing import Any
from dataclasses import dataclass
import json
@dataclass
class ExternalUrls:
    spotify: str

    @staticmethod
    def from_dict(obj: Any) -> 'ExternalUrls':
        _spotify = str(obj.get("spotify"))
        return ExternalUrls(_spotify)

@dataclass
class Followers:
    href: str
    total: int

    @staticmethod
    def from_dict(obj: Any) -> 'Followers':
        _href = str(obj.get("href"))
        _total = int(obj.get("total"))
        return Followers(_href, _total)

@dataclass
class Image:
    url: str
    height: int
    width: int

    @staticmethod
    def from_dict(obj: Any) -> 'Image':
        _url = str(obj.get("url"))
        _height = int(obj.get("height"))
        _width = int(obj.get("width"))
        return Image(_url, _height, _width)

@dataclass
class Owner:
    external_urls: ExternalUrls
    followers: Followers
    href: str
    id: str
    type: str
    uri: str
    display_name: str

    @staticmethod
    def from_dict(obj: Any) -> 'Owner':
        _external_urls = ExternalUrls.from_dict(obj.get("external_urls"))
        try:
            _followers = Followers.from_dict(obj.get("followers"))
        except Exception as err:
            _followers = None
        _href = str(obj.get("href"))
        _id = str(obj.get("id"))
        _type = str(obj.get("type"))
        _uri = str(obj.get("uri"))
        _display_name = str(obj.get("display_name"))
        return Owner(_external_urls, _followers, _href, _id, _type, _uri, _display_name)

@dataclass
class Tracks:
    href: str
    total: int

    @staticmethod
    def from_dict(obj: Any) -> 'Tracks':
        _href = str(obj.get("href"))
        _total = int(obj.get("total"))
        return Tracks(_href, _total)
    
    
@dataclass
class Playlist:
    collaborative: bool
    description: str
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    owner: Owner
    public: bool
    snapshot_id: str
    tracks: Tracks
    type: str
    uri: str

    @staticmethod
    def from_dict(obj: Any) -> 'Playlist':
        _collaborative = bool(obj.get("public"))
        _description = str(obj.get("description"))
        _external_urls = ExternalUrls.from_dict(obj.get("external_urls"))
        _href = str(obj.get("href"))
        _id = str(obj.get("id"))
        _images = [Image.from_dict(y) for y in obj.get("images")]
        _name = str(obj.get("name"))
        _owner = Owner.from_dict(obj.get("owner"))
        _public = bool(obj.get("public"))
        _snapshot_id = str(obj.get("snapshot_id"))
        _tracks = Tracks.from_dict(obj.get("tracks"))
        _type = str(obj.get("type"))
        _uri = str(obj.get("uri"))
        return Playlist(_collaborative, _description, _external_urls, _href, _id, _images, _name, _owner, _public, _snapshot_id, _tracks, _type, _uri)



# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Playlist.from_dict(jsonstring)
