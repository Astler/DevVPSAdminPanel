import json
from typing import Any, List


class BannerFirebaseItem:
    def __init__(self, daily_date: int, author: str, author_id: str, banner_name: str,
                 banner_sources: str, banner_tags: List[str], chosen_by_developers: bool,
                 mdate: int, mid: str, mlayers: List[dict], likes_array: List[str],
                 tags: List[str], total_likes: int, unique_banner_code: str):
        self.daily_date = daily_date
        self.author = author
        self.author_id = author_id
        self.banner_name = banner_name
        self.banner_sources = banner_sources
        self.banner_tags = banner_tags
        self.chosen_by_developers = chosen_by_developers
        self.mdate = mdate
        self.mid = mid
        self.layers = mlayers
        self.likes_array = likes_array
        self.tags = tags
        self.unique_banner_code = unique_banner_code
        self.total_likes = total_likes

    @classmethod
    def from_json(cls, doc_json: str) -> 'BannerFirebaseItem':
        try:
            doc_dict = json.loads(doc_json)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
        return cls.from_dict(doc_dict)

    @classmethod
    def from_dict(cls, doc_dict: dict) -> 'BannerFirebaseItem':
        daily_date = doc_dict.get('dailyDate', 0)
        author = doc_dict.get('mauthor', '')
        author_id = doc_dict.get('mauthorId', '')
        banner_name = doc_dict.get('mbannerName', '')
        banner_sources = doc_dict.get('mbannerSources', '')
        banner_tags = doc_dict.get('mbannerTags', [])
        chosen_by_developers = doc_dict.get('mchosenByDevelopers', False)
        mdate = doc_dict.get('mdate', 0)
        mid = doc_dict.get('mid', '')
        unique_banner_code = doc_dict.get('moriginalLayersCode', '')
        mlayers = doc_dict.get('mlayers', [])
        likes_array = doc_dict.get('mlikesArray', [])
        tags = doc_dict.get('mtags', [])
        total_likes = doc_dict.get('mtotalLikes', 0)

        # Create an instance of BannerFirebaseItem with the extracted values
        return cls(daily_date, author, author_id, banner_name, banner_sources,
                   banner_tags, chosen_by_developers, mdate, mid, mlayers,
                   likes_array, tags, total_likes, unique_banner_code)
