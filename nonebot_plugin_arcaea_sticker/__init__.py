from typing import List, Optional
from nonebot import require, logger, get_driver
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText
from nonebot.typing import T_State
from nonebot.exception import FinishedException
from nonebot.adapters import Event

require("nonebot_plugin_alconna")
require("nonebot_plugin_htmlrender")

from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    Args,
    Option,
    Arparma,
    UniMessage,
    MultiVar,
)

from .config import Config, plugin_config, RESOURCE_DIR, FONT_DIR
from .resource import ResourceManager
from .render import generate_sticker_image, renderer, resource_manager
from .help import generate_help_image, HELP_TEXT

driver = get_driver()

def normalize_color(color: str) -> str:
    """标准化颜色格式（添加#前缀）"""
    return color if color.startswith('#') else f"#{color}"

def auto_darken_color(color: str, factor: float = 0.7) -> str:
    """自动生成更深的颜色（用于描边）"""
    try:
        color = normalize_color(color)
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, IndexError):
        return "#ffffff"

def auto_wrap_text(text: str, max_length: int = 20) -> str:
    """自动换行长文本"""
    if len(text) <= max_length or '\n' in text:
        return text
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in text.split():
        if current_length + len(word) > max_length:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)

__version__ = "0.4.0"

__plugin_meta__ = PluginMetadata(
    name="Arcaea表情包生成器",
    description="生成Arcaea风格的表情包（跨平台支持）",
    usage=(
        "arc -h 查看文本帮助\n"
        "arc帮助 查看图片帮助\n"
        "arc 进入交互模式\n"
        "arc <角色> <文字> 快速生成"
    ),
    type="application",
    homepage="https://github.com/JQ-28/nonebot-plugin-arcaea-sticker",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "author": "JQ-28",
        "version": __version__,
        "priority": 1,
    },
)

arc_cmd = Alconna(
    "arc",
    Args["text", MultiVar(str, "*")],
    Option("-i|--id", Args["id", str], help_text="表情 ID，不提供时则随机选择"),
    Option("-n|--name", Args["name", str], help_text="角色名称，例如 luna，与 -i 参数二选一"),
    Option("-x", Args["x", int], help_text="文字的中心 x 坐标"),
    Option("-y", Args["y", int], help_text="文字的中心 y 坐标"),
    Option("-r|--rotate", Args["rotate", float], help_text="文字旋转的角度"),
    Option("-s|--size", Args["size", int], help_text="文字的大小"),
    Option("-c|--color", Args["color", str], help_text="文字颜色，使用 16 进制格式"),
    Option("-w|--stroke-width", Args["stroke_width", int], help_text="文本描边宽度"),
    Option("-C|--stroke-color", Args["stroke_color", str], help_text="文本描边颜色，使用 16 进制格式"),
)

arc = on_alconna(
    arc_cmd,
    aliases={"arcaea"},
    priority=11,
    block=True,
)

from nonebot import on_command

arc_help = on_command("arc帮助", aliases={"arcaea帮助"}, priority=11, block=True)

@arc_help.handle()
async def show_help_image():
    """显示帮助图片"""
    try:
        logger.info("生成帮助图片...")
        help_image = await generate_help_image()
        logger.info(f"帮助图片生成成功，大小: {len(help_image)} bytes")
        await UniMessage.image(raw=help_image).finish(at_sender=plugin_config.arcaea_reply)
    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"生成帮助图片失败: {e}")
        await UniMessage.text(HELP_TEXT).finish(at_sender=plugin_config.arcaea_reply)

@arc.handle()
async def handle_args(matcher: Matcher, result: Arparma):
    """处理命令参数,生成表情"""
    text_arg = result.all_matched_args.get("text", ())
    if not text_arg or len(text_arg) == 0:
        matcher.skip()
        return
    
    try:
        sticker_id_opt = result.query[str]("id.id")
        sticker_name_opt = result.query[str]("name.name")
        
        if sticker_id_opt and sticker_name_opt:
            await UniMessage.text("不能同时用 -i 和 -n 参数").finish(at_sender=plugin_config.arcaea_reply)
        
        identifier = sticker_id_opt or sticker_name_opt or (text_arg[0] if len(text_arg) > 0 else None)
        
        text = ""
        if len(text_arg) > 1:
            text = " ".join(text_arg[1:])
            
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            
            text = text.replace('\\n', '\n').replace('\\\\n', '\\n').strip()
            text = auto_wrap_text(text)
        
        if not identifier:
            await UniMessage.text("请指定表情名称或ID").finish(at_sender=plugin_config.arcaea_reply)
        
        selected_sticker = resource_manager.select_sticker(identifier)
        if not selected_sticker:
            await UniMessage.text("没有找到对应的表情").finish(at_sender=plugin_config.arcaea_reply)

        if not text:
            await UniMessage.text("文本内容不能为空").finish(at_sender=plugin_config.arcaea_reply)

        params = {}
        
        if size_val := result.query[int]("size.size"):
            params["font_size"] = size_val
            logger.debug(f"设置字体大小: {params['font_size']}")
        
        if color_val := result.query[str]("color.color"):
            params["font_color"] = normalize_color(color_val)
            params["stroke_color"] = auto_darken_color(color_val)
        
        if x_val := result.query[int]("x.x"):
            params["x"] = x_val
        
        if y_val := result.query[int]("y.y"):
            params["y"] = y_val
        
        if rotate_val := result.query[float]("rotate.rotate"):
            params["rotate"] = rotate_val
        
        if width_val := result.query[int]("stroke-width.stroke_width"):
            params["stroke_width"] = width_val
        
        if stroke_val := result.query[str]("stroke-color.stroke_color"):
            params["stroke_color"] = normalize_color(stroke_val)

        try:
            image = await generate_sticker_image(
                selected_sticker,
                text,
                auto_adjust=True,
                **params
            )
            logger.debug(f"生成表情图片参数: {params}")
        except Exception as e:
            logger.exception("生成表情图片失败")
            await UniMessage.text(f"生成表情图片失败: {str(e)}").finish(at_sender=plugin_config.arcaea_reply)

        await UniMessage.image(raw=image).finish(at_sender=plugin_config.arcaea_reply)

    except Exception as e:
        logger.opt(exception=e).debug("处理出错")
        await matcher.finish()

@arc.handle()
async def handle_first_msg(matcher: Matcher, state: T_State):
    """处理第一条消息"""
    try:
        image = await resource_manager.get_all_characters_grid()
        msg = (
            UniMessage.image(raw=image) + 
            UniMessage.text(
                "请发送你要生成表情的角色名称，或者直接发送表情 ID，或者发送 `随机` 使用一张随机表情\n"
                "Tip：你可以随时发送 `0` 退出交互模式"
            )
        )
        await msg.send(at_sender=plugin_config.arcaea_reply)
    except Exception as e:
        await UniMessage.text(f"获取角色列表出错:\n{e}").finish(at_sender=plugin_config.arcaea_reply)

@arc.got("character")
async def handle_character(matcher: Matcher, state: T_State, arg: str = ArgPlainText("character")):
    """处理角色选择"""
    if arg in ("0", "q", "e", "quit", "exit", "退出"):
        await UniMessage.text("已退出交互模式").finish(at_sender=plugin_config.arcaea_reply)
        
    sticker_info = resource_manager.select_sticker(arg)
    if not sticker_info:
        await matcher.reject("没有找到对应的表情,请重新输入")
        
    state["sticker_info"] = sticker_info
    await UniMessage.text("请发送要添加的文字").send(at_sender=plugin_config.arcaea_reply)

@arc.got("text")
async def handle_text(matcher: Matcher, state: T_State, text: str = ArgPlainText("text")):
    """处理文字输入"""
    sticker_info = state["sticker_info"]
    text = text.replace("\\n", "\n").strip()
    
    try:
        image = await generate_sticker_image(sticker_info, text, auto_adjust=True)
    except Exception as e:
        logger.exception("生成表情出错")
        await UniMessage.text(f"生成表情出错: {e}").finish(at_sender=plugin_config.arcaea_reply)
        
    await UniMessage.image(raw=image).send(at_sender=plugin_config.arcaea_reply)
    await matcher.finish()