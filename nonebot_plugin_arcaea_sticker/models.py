from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from pathlib import Path

from .config import CHARACTER_COLORS, DEFAULT_COLORS

class TextConfig(BaseModel):
    """文本配置基类"""
    x: int = Field(default=148, ge=0, le=296, description="文字X坐标")
    y: int = Field(default=128, ge=0, le=256, description="文字Y坐标")
    rotate: float = Field(default=-12, ge=-180, le=180, description="文字旋转角度")
    font_size: int = Field(default=35, ge=10, le=100, description="文字大小")
    stroke_width: int = Field(default=8, ge=0, le=20, description="描边宽度")

    class Config:
        validate_assignment = True

class StickerText(TextConfig):
    """表情文字配置"""
    text: str = Field(..., description="文字内容")
    inner_stroke_width: int = Field(default=4, ge=0, le=10, description="内层描边宽度")
    inner_stroke_color: Optional[str] = Field(None, description="内层描边颜色")
    stroke_color: str = Field(default="#ffffff", description="描边颜色")

    @validator('stroke_color', 'inner_stroke_color')
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """验证颜色格式"""
        if v and not v.startswith('#'):
            v = f"#{v}"
        return v

class StickerInfo(BaseModel):
    """表情信息"""
    sticker_id: str = Field(..., description="表情ID")
    name: str = Field(..., description="角色名称")
    character: str = Field(..., description="角色标识符")
    img: str = Field(..., description="图片文件名")
    fill_color: str = Field(..., description="文字填充颜色")
    inner_stroke_color: Optional[str] = Field(None, description="内层描边颜色")
    stroke_color: str = Field(default="#ffffff", description="描边颜色")
    default_text: StickerText = Field(..., description="默认文本配置")

    class Config:
        validate_assignment = True

    @validator('fill_color', 'stroke_color', 'inner_stroke_color')
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """验证颜色格式"""
        if v and not v.startswith('#'):
            v = f"#{v}"
        return v

    def get_image_path(self, resource_dir: Path) -> Path:
        """获取图片完整路径"""
        return resource_dir / self.img

    def get_render_params(self, text: str, **params: Dict[str, Any]) -> Dict[str, Any]:
        """获取渲染参数"""
        return {
            "text": text,
            "x": params.get("x", self.default_text.x),
            "y": params.get("y", self.default_text.y),
            "font_size": params.get("font_size", self.default_text.font_size),
            "rotate": params.get("rotate", self.default_text.rotate),
            "font_color": params.get("font_color", self.fill_color),
            "stroke_color": params.get("stroke_color", self.stroke_color),
            "stroke_width": params.get("stroke_width", self.default_text.stroke_width),
        }

    @classmethod
    def create(cls, sticker_id: str, name: str, img: str) -> 'StickerInfo':
        """创建表情信息"""
        colors = CHARACTER_COLORS.get(name.lower(), DEFAULT_COLORS)
        
        return cls(
            sticker_id=sticker_id,
            name=name,
            character=name.lower(),
            img=img,
            fill_color=colors["fill"],
            stroke_color=colors["stroke"],
            default_text=StickerText(
                text="Arcaea",
                x=145,
                y=50,
                rotate=-12,
                font_size=35
            )
        )