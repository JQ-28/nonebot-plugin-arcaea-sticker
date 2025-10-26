import random
from pathlib import Path
from typing import List, Optional, Dict
from nonebot import logger
import anyio

from .config import CHARACTER_ID_MAP
from .models import StickerInfo

class CharacterManager:
    """角色管理器"""
    def __init__(self):
        self.characters: List[StickerInfo] = []
        self.name_mapping: Dict[str, str] = {
            "露娜": "luna",
            "光": "hikari",
            "光光": "hikari",
            "光2": "hikari2",
            "光光2": "hikari2",
            "依利丝": "ilith",
            "洞烛": "insight",
            "群愿": "kanae",
            "红": "kou",
            "红红": "kou",
            "拉格兰": "lagrange",
            "忘却": "lethe",
            "摩耶": "maya",
            "奈美": "nami",
            "咲弥": "saya",
            "白姬": "shirahime",
            "对立": "tairitsu",
            "病女": "tairitsu2",
            "病女对立": "tairitsu2",
            "对立2": "tairitsu2",
            "对立3": "tairitsu3",
            "风暴对立": "tairitsu3",
            "猫对立": "tairitsu3",
            "维塔": "vita",
            "ai酱": "aichan",
            "彩梦": "ayu",
            "爱托": "eto"
        }
    
    def add_character(self, character: StickerInfo):
        """添加角色"""
        self.characters.append(character)
    
    def get_random(self) -> Optional[StickerInfo]:
        """获取随机角色"""
        return random.choice(self.characters) if self.characters else None
    
    def find_by_name(self, name: str) -> Optional[StickerInfo]:
        """通过名称查找角色"""
        name = name.lower()
        if name in self.name_mapping:
            name = self.name_mapping[name]
        return next((x for x in self.characters if x.name.lower() == name), None)
    
    def find_by_id(self, id_str: str) -> Optional[StickerInfo]:
        """通过ID查找角色"""
        return next((x for x in self.characters if x.sticker_id == id_str), None)
    
    def select_character(self, identifier: Optional[str] = None) -> Optional[StickerInfo]:
        """选择角色"""
        if not identifier:
            return None
        
        if identifier in ("random", "随机"):
            return self.get_random()
        
        character = self.find_by_name(identifier)
        if character:
            return character
        
        if identifier in CHARACTER_ID_MAP:
            return self.find_by_id(CHARACTER_ID_MAP[identifier])
        
        if identifier.isdigit():
            return self.find_by_id(identifier)
        
        return None

class ResourceManager:
    """资源管理器"""
    def __init__(self, resource_dir: Path):
        self.resource_dir = resource_dir
        self.character_manager = CharacterManager()
        self._load_characters()
    
    def _load_characters(self):
        """加载角色信息"""
        try:
            if not self.resource_dir.exists():
                raise FileNotFoundError(f"资源目录不存在: {self.resource_dir}")
            
            sticker_files = sorted(
                f.name for f in self.resource_dir.glob("*.png") 
                if f.name != "arcaea_stickers.png"
            )
            
            if not sticker_files:
                raise FileNotFoundError(f"没有找到任何角色图片: {self.resource_dir}")
            
            for filename in sticker_files:
                name = filename.replace(".png", "")
                character = name.lower()
                sticker_id = CHARACTER_ID_MAP.get(character, "0")
                
                sticker = StickerInfo.create(
                    sticker_id=sticker_id,
                    name=name,
                    img=filename
                )
                self.character_manager.add_character(sticker)
            
            logger.info(f"已加载 {len(self.character_manager.characters)} 个角色")
        except Exception as e:
            logger.error(f"加载角色信息失败: {e}")
            raise
    
    async def read_image(self, path: Path) -> bytes:
        """读取图片文件"""
        try:
            return await anyio.Path(path).read_bytes()
        except Exception as e:
            logger.exception(f"读取图片失败: {path}")
            raise FileNotFoundError(f"无法读取图片: {e}")
    
    def get_resource_path(self, name: str) -> Path:
        """获取资源文件路径"""
        path = self.resource_dir / name
        if not path.exists():
            raise FileNotFoundError(f"资源文件不存在: {name}")
        return path
    
    async def load_resource(self, name: str) -> bytes:
        """加载资源文件"""
        path = self.get_resource_path(name)
        return await self.read_image(path)
    
    async def get_all_characters_grid(self) -> bytes:
        """获取所有角色列表图片"""
        try:
            path = self.resource_dir / "arcaea_stickers.png"
            if not path.exists():
                raise FileNotFoundError(f"找不到角色列表图片: {path}")
            return await self.read_image(path)
        except Exception as e:
            logger.exception(f"获取角色列表图片失败: {e}")
            raise

    def select_sticker(self, identifier: Optional[str] = None) -> Optional[StickerInfo]:
        """选择表情"""
        return self.character_manager.select_character(identifier)