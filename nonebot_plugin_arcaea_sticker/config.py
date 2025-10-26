from pathlib import Path
from typing import List, Optional
from nonebot import get_plugin_config, require

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

from pydantic import BaseModel

PLUGIN_DIR = Path(__file__).parent
RESOURCE_DIR = PLUGIN_DIR / "img"
FONT_DIR = PLUGIN_DIR / "fonts"
DATA_DIR = store.get_plugin_data_dir() / "arcaea_sticker"

def ensure_data_dir():
    """确保数据目录存在（懒加载）"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR

# 角色ID映射表
CHARACTER_ID_MAP = {
    "luna": "12",
    "aichan": "1",
    "ayu": "2",
    "eto": "3",
    "hikari": "4",
    "hikari2": "5",
    "ilith": "6",
    "insight": "7",
    "kanae": "8",
    "kou": "9",
    "lagrange": "10",
    "lethe": "11",
    "maya": "13",
    "nami": "14",
    "nonoka": "15",
    "saya": "16",
    "shirabe": "17",
    "shirahime": "18",
    "tairitsu": "19",
    "tairitsu2": "20",
    "tairitsu3": "21",
    "vita": "22",
    "ai酱": "1",
    "彩梦": "2",
    "爱托": "3",
    "光": "4",
    "光光": "4",
    "光2": "5",
    "光光2": "5",
    "依利丝": "6",
    "洞烛": "7",
    "群愿": "8",
    "红": "9",
    "红红": "9",
    "拉格兰": "10",
    "忘却": "11",
    "露娜": "12",
    "摩耶": "13",
    "奈美": "14",
    "野乃香": "15",
    "咲弥": "16",
    "白姬": "18",
    "对立": "19",
    "病女": "20",
    "病女对立": "20",
    "对立2": "20",
    "对立3": "21",
    "风暴对立": "21",
    "猫对立": "21",
    "维塔": "22",
}

CHARACTER_COLORS = {
    "ayu": {"fill": "#3BEADF", "stroke": "#30bbb2"},
    "eto": {"fill": "#79cfe8", "stroke": "#0b8eb7"},
    "hikari": {"fill": "#ffe7b5", "stroke": "#ef7d04"},
    "hikari2": {"fill": "#ffe7b5", "stroke": "#ef7d04"},
    "ilith": {"fill": "#f58194", "stroke": "#c61632"},
    "kou": {"fill": "#ffd5d5", "stroke": "#f04f87"},
    "lagrange": {"fill": "#bbd7fa", "stroke": "#4c8cdd"},
    "luna": {"fill": "#c09edd", "stroke": "#7743a3"},
    "maya": {"fill": "#E8B088", "stroke": "#C17F59"},
    "nami": {"fill": "#f9c2cb", "stroke": "#f62f51"},
    "shirahime": {"fill": "#c3d5ff", "stroke": "#657ae7"},
    "shirabe": {"fill": "#e5616d", "stroke": "#974149"},
    "tairitsu": {"fill": "#80e8d5", "stroke": "#329f8c"},
    "tairitsu2": {"fill": "#80e8d5", "stroke": "#329f8c"},
    "tairitsu3": {"fill": "#80e8d5", "stroke": "#329f8c"},
    "vita": {"fill": "#f58194", "stroke": "#c81c38"},
    "kanae": {"fill": "#fbd0ad", "stroke": "#FFB87F"},
    "saya": {"fill": "#80e8d5", "stroke": "#329f8c"},
    "lethe": {"fill": "#F6D3C2", "stroke": "#E3BAA7"},
    "insight": {"fill": "#C9CBEA", "stroke": "#a8a9c3"},
    "aichan": {"fill": "#CDB4E8", "stroke": "#a28fb6"},
    "nonoka": {"fill": "#eee1af", "stroke": "#beb48c"},
}

DEFAULT_COLORS = {
    "fill": "#ffffff",
    "stroke": "#ffffff"
}

class Config(BaseModel):
    """插件配置"""
    arcaea_reply: bool = True

plugin_config = get_plugin_config(Config)