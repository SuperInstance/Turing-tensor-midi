"""Skills sub-package — individual voice command capabilities."""

from .web import WebSkill
from .weather import WeatherSkill
from .news import NewsSkill
from .music import MusicSkill
from .system import SystemSkill
from .band import BandSkill

__all__ = ["WebSkill", "WeatherSkill", "NewsSkill", "MusicSkill", "SystemSkill", "BandSkill"]
