"""
HiddenGem – Graph Node Models
-------------------------------
Plain Python dataclasses that represent each Neo4j node type.
These are used for type-safety and documentation — they are NOT
ORM models; the actual database work happens in schema.py.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Destination:
    """A tourism spot in Karnataka (e.g. Coorg, Hampi, Jog Falls)."""
    name: str
    description: str        = ""
    category: str           = ""   # e.g. "Nature", "Heritage", "Adventure"
    latitude: float         = 0.0
    longitude: float        = 0.0
    best_season: str        = ""   # e.g. "October to February"
    image_url: str          = ""


@dataclass
class District:
    """An administrative district of Karnataka (e.g. Mysuru, Kodagu)."""
    name: str


@dataclass
class Attraction:
    """A specific attraction inside or near a Destination."""

    name: str

    attraction_type: str = ""
    description: str = ""

    # Itinerary data
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # 24-hour format, e.g. "10:00", "17:30"
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None

@dataclass
class Activity:
    """A tourist activity available at a Destination (e.g. trekking, camping)."""
    name: str
    activity_type: str      = ""   # e.g. "Adventure", "Leisure"
    difficulty: str         = ""   # e.g. "Easy", "Moderate", "Hard"


@dataclass
class Food:
    """A local dish or food item associated with a Destination (e.g. Mysuru Pak)."""
    name: str
    food_type: str          = ""   # e.g. "Street Food", "Traditional"
    is_vegetarian: bool     = True


@dataclass
class Hashtag:
    """A social-media hashtag used to tag travel content (e.g. #KarnatakaTourism)."""
    tag: str                       # stored without '#', e.g. "KarnatakaTourism"


@dataclass
class TravelContent:
    """A piece of user-generated content (blog post, reel, tweet) about a destination."""
    url: str
    platform: str           = ""   # e.g. "Instagram", "YouTube", "Blog"
    title: str              = ""
    posted_at: str          = ""   # ISO date string, e.g. "2024-01-15"


@dataclass
class Review:
    """A traveller review of a Destination."""
    review_id: str
    text: str               = ""
    rating: float           = 0.0  # 1.0 – 5.0
    author: str             = ""
    created_at: str         = ""   # ISO date string
