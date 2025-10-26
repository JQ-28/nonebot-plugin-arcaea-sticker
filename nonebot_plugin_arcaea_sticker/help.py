"""Arcaea 表情包帮助文档"""
from pathlib import Path
from typing import Optional

from nonebot import logger, require

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import get_new_page

from .config import FONT_DIR
from .render import ImageRenderer

TEMPLATES_DIR = Path(__file__).parent / "templates"
renderer = ImageRenderer(TEMPLATES_DIR)

class HelpRenderer:
    """帮助文档渲染器"""
    def __init__(self):
        self.template = renderer.env.get_template("help.svg.jinja")
    
    async def render_help_svg(self) -> str:
        """渲染帮助SVG"""
        params = {
            "font": renderer.to_router_url(FONT_DIR / "YurukaFangTang.ttf"),
        }
        return await self.template.render_async(**params)
    
    async def render_to_png(self, svg: str) -> bytes:
        """将SVG渲染为PNG"""
        async with get_new_page(viewport={'width': 800, 'height': 750, 'deviceScaleFactor': 2}) as page:
            await page.set_content(svg)
            element = await page.query_selector("svg")
            if not element:
                raise ValueError("无法找到SVG元素")
            return await element.screenshot(
                type="png",
                omit_background=True
            )

help_renderer = HelpRenderer()

async def generate_help_image() -> bytes:
    """生成帮助图片
    
    Returns:
        bytes: PNG格式的帮助图片数据
        
    Raises:
        Exception: 当图片生成失败时抛出异常
    """
    try:
        svg = await help_renderer.render_help_svg()
        return await help_renderer.render_to_png(svg)
    except Exception as e:
        logger.exception("生成帮助图片失败")
        raise Exception(f"生成帮助图片失败: {str(e)}")

HELP_TEXT = """Arcaea 表情包生成器

基础用法：
  arc <角色> <文字>
  例如：arc luna 好耶！
  或者：arc 7 开心

进阶用法：
  1. 使用角色名：arc luna/hikari/eto/ayu...
  2. 使用角色ID：arc 1-21 (每个角色都有固定ID)
  3. 随机角色：arc random/随机
  4. 多行文字：使用\\n换行，如 arc luna "第一行\\n第二行"

自定义参数（都是可选的）：
  -s, --size <大小>     文字大小 (10~100，默认45)
                      数字越大文字越大
  
  -x <位置>            横向位置 (0~296，默认148)
                      数字越大文字越靠右
                      0在最左边，296在最右边
  
  -y <位置>            纵向位置 (0~256，默认128)
                      数字越大文字越靠下
                      0在最上面，256在最下面
  
  -r, --rotate <角度>   旋转角度 (-180~180，默认-12)
                      正数顺时针旋转，负数逆时针旋转
                      如 -r 45 向右倾斜，-r -45 向左倾斜
  
  -c, --color <颜色>    文字颜色 (使用十六进制，如 #FF0000)
                      常用颜色：
                      #FF0000 红色   #00FF00 绿色
                      #0000FF 蓝色   #FFFF00 黄色
                      #FF00FF 粉色   #FFFFFF 白色
  
  -w, --stroke-width <宽度>  描边宽度 (0~20，默认8)
                           数字越大描边越粗
  
  -C, --stroke-color <颜色>  描边颜色 (同文字颜色格式)

使用示例：
  arc luna 好耶！                         # 基础用法
  arc hikari "努力\\n学习"                 # 多行文字
  arc tairitsu 开心 -x 150 -y 100 -r -20  # 调整位置和角度
  arc eto 可爱 -c #FF69B4 -s 60           # 修改颜色和大小
  arc random 摸鱼中...                    # 随机角色

Made with love by JQ-28
""" 