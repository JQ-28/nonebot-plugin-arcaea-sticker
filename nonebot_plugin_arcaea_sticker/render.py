import math
from pathlib import Path
from typing import Optional, Union, Dict
from contextlib import asynccontextmanager

from nonebot import logger, require
from playwright.async_api import Page, Route, Request
import anyio
import jinja2
from yarl import URL

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import get_new_page

from .config import FONT_DIR, RESOURCE_DIR, PLUGIN_DIR
from .models import StickerInfo, StickerText
from .text import TextSizeCalculator
from .resource import ResourceManager

DEFAULT_WIDTH = 296
DEFAULT_HEIGHT = 256
DEFAULT_STROKE_WIDTH = 9
DEFAULT_LINE_SPACING = 1.3
DEFAULT_STROKE_COLOR = "#ffffff"
ROUTER_BASE_URL = "https://arcaea.nonebot/"
TEMPLATES_DIR = PLUGIN_DIR / "templates"

class ImageRenderer:
    """处理表情图片的渲染"""
    
    def __init__(self, templates_dir: Path) -> None:
        """初始化渲染器,设置模板目录"""
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            enable_async=True,
        )
        self.text_calculator = TextSizeCalculator(
            max_width=DEFAULT_WIDTH,
            max_height=DEFAULT_HEIGHT
        )
    
    def to_router_url(self, path: Union[str, Path]) -> str:
        """把本地路径转成路由URL"""
        if not isinstance(path, Path):
            path = Path(path)
        
        # 不再使用 relative_to，直接使用文件名
        url = f"{ROUTER_BASE_URL}{path.name}".replace("\\", "/")
        return url
    
    async def render_svg(self, info: StickerInfo, text: str, **params) -> str:
        """渲染SVG模板"""
        try:
            # 使用新的 get_render_params 方法获取渲染参数
            render_params = info.get_render_params(text, **params)
            
            # 添加其他必要参数
            template_params = {
                "id": hash(info.img),
                "image": self.to_router_url(info.get_image_path(RESOURCE_DIR)),
                "font": self.to_router_url(FONT_DIR / "YurukaFangTang.ttf"),
                "width": DEFAULT_WIDTH,
                "height": DEFAULT_HEIGHT,
                "line_spacing": params.get("line_spacing", DEFAULT_LINE_SPACING),
                **render_params
            }
            
            template = self.env.get_template("sticker.svg.jinja")
            return await template.render_async(**template_params)
        except Exception as e:
            logger.exception("SVG渲染失败")
            raise RuntimeError(f"SVG渲染失败: {e}")
    
    async def render_to_png(self, svg: str) -> bytes:
        """将SVG渲染为PNG"""
        try:
            async with get_routed_page(svg) as page:
                element = await page.query_selector("svg")
                if not element:
                    raise ValueError("无法找到SVG元素")
                return await element.screenshot(
                    type="png",
                    omit_background=True,
                    scale="device"
                )
        except Exception as e:
            logger.exception("PNG渲染失败")
            raise RuntimeError(f"PNG渲染失败: {e}")
    
    async def render(self, info: StickerInfo, text: str, **params) -> bytes:
        """渲染表情图片"""
        try:
            # 只在明确要求自动调整时才进行调整
            if params.get("auto_adjust", False):
                font_size = self.text_calculator.calc_text_size(
                    text,
                    info.default_text.font_size,  # 使用默认大小作为基准
                    params.get("rotate", info.default_text.rotate)
                )
                params["font_size"] = font_size
            elif "font_size" not in params:
                # 如果没有手动设置字体大小且不需要自动调整，使用默认值
                params["font_size"] = info.default_text.font_size
            
            # 渲染SVG
            svg = await self.render_svg(info, text, **params)
            
            # 转换为PNG
            return await self.render_to_png(svg)
        except Exception as e:
            logger.exception("表情图片渲染失败")
            raise RuntimeError(f"表情图片渲染失败: {e}")

renderer = ImageRenderer(TEMPLATES_DIR)
resource_manager = ResourceManager(RESOURCE_DIR)

async def file_router(route: Route, request: Request):
    """文件路由处理"""
    try:
        url = URL(request.url)
        filename = url.path.split('/')[-1]
        
        search_paths = [
            RESOURCE_DIR / filename,
            FONT_DIR / filename,
            PLUGIN_DIR / "img" / filename,
            PLUGIN_DIR / "fonts" / filename,
        ]
        
        for path in search_paths:
            if path.exists():
                data = await anyio.Path(path).read_bytes()
                await route.fulfill(body=data)
                return
                
        raise FileNotFoundError(f"File not found: {filename}")
    except Exception as e:
        logger.exception(f"File loading error: {e}")
        await route.abort()

@asynccontextmanager
async def get_routed_page(initial_html: Optional[str] = None):
    """获取带路由的页面"""
    async with get_new_page(
        viewport={'width': DEFAULT_WIDTH, 'height': DEFAULT_HEIGHT, 'deviceScaleFactor': 2}
    ) as page:
        await page.route(f"{ROUTER_BASE_URL}**/*", file_router)
        
        if initial_html:
            await page.set_content(initial_html)
        
        yield page

async def generate_sticker_image(
    info: StickerInfo,
    text: str,
    **params
) -> bytes:
    """生成表情图片"""
    try:
        return await renderer.render(info, text, **params)
    except Exception as e:
        logger.exception("生成表情图片失败")
        raise Exception(f"生成表情图片失败: {str(e)}")