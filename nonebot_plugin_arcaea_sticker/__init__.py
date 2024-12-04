from typing import List, Optional
from nonebot import require, logger, get_driver
from nonebot.plugin import PluginMetadata
from nonebot.rule import ArgumentParser, Namespace
from nonebot import on_command, on_shell_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import Arg, ArgPlainText, CommandArg, ShellCommandArgs
from nonebot.typing import T_State
from nonebot.exception import ParserExit, FinishedException
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent

require("nonebot_plugin_htmlrender")

from .config import Config, plugin_config, RESOURCE_DIR, FONT_DIR
from .resource import ResourceManager
from .render import generate_sticker_image, renderer, resource_manager
from .help import generate_help_image, HELP_TEXT

# 获取驱动器
driver = get_driver()

__version__ = "0.2.6"

__plugin_meta__ = PluginMetadata(
    name="Arcaea表情包生成器",
    description="生成Arcaea风格的表情包",
    usage="发送 arc -h 查看帮助",
    type="application",
    homepage="https://github.com/JQ-28/nonebot-plugin-arcaea-sticker",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={
        "author": "JQ-28",
        "version": "0.2.6",
        "priority": 1,
    },
)

# 创建命令解析器
cmd_parser = ArgumentParser("arc", description="Arcaea 表情包生成器")
cmd_parser.add_argument("text", nargs="*", help="添加的文字，为空时使用默认值", type=str)
cmd_parser.add_argument(
    "-i", 
    "--id", 
    help="表情 ID，不提供时则随机选择"
)
cmd_parser.add_argument(
    "-n",
    "--name",
    help="角色名称，例如 luna，与 -i 参数二选一"
)
cmd_parser.add_argument(
    "-x",
    "--x",
    help="文字的中心 x 坐标"
)
cmd_parser.add_argument(
    "-y",
    "--y",
    help="文字的中心 y 坐标"
)
cmd_parser.add_argument(
    "-r",
    "--rotate",
    help="文字旋转的角度"
)
cmd_parser.add_argument(
    "-s",
    "--size",
    help="文字的大小"
)
cmd_parser.add_argument(
    "-c",
    "--color",
    dest="font_color",
    help="文字颜色，使用 16 进制格式"
)
cmd_parser.add_argument(
    "-w",
    "--stroke-width",
    help="文本描边宽度"
)
cmd_parser.add_argument(
    "-C",
    "--stroke-color",
    help="文本描边颜色，使用 16 进制格式"
)

# 注册命令
arc = on_shell_command(
    "arc",
    parser=cmd_parser,
    aliases={"arcaea"},
)

# 处理帮助信息（放在最前面）
@arc.handle()
async def handle_help(matcher: Matcher, args: ParserExit = ShellCommandArgs()):
    # 只处理帮助命令
    if not isinstance(args, ParserExit) or args.status != 0:
        return

    try:
        # 尝试生成并发送帮助图片
        help_image = await generate_help_image()
        msg = MessageSegment.image(help_image)
    except Exception as e:
        # 如果图片生成失败，使用文字帮助
        logger.exception("生成帮助图片出错")
        msg = HELP_TEXT

    # 发送帮助信息
    if plugin_config.arcaea_reply:
        await matcher.finish(msg, at_sender=True)
    else:
        await matcher.finish(msg)

# 处理命令行参数
@arc.handle()
async def handle_args(matcher: Matcher, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    if not any(vars(args).values()) or (len(args.text) == 0):
        matcher.skip()
        return
    
    try:
        # 处理 ID 或名称
        sticker_id: Optional[str] = args.id
        sticker_name: Optional[str] = args.name
        
        if sticker_id and sticker_name:
            await matcher.finish("不能同时使用 -i 和 -n 参数")
        
        # 获取原始消息文本
        raw_message = str(event.message)
        
        # 提取角色标识符
        identifier = sticker_id or sticker_name or args.text[0]
        
        # 提取文本内容
        if len(args.text) > 1:
            # 获取原始文本
            text = " ".join(args.text[1:])
            
            # 检查是否是带引号的文本
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]  # 移除引号
            
            # 统一处理换行符
            text = text.replace('\\n', '\n')  # 处理显式的换行符
            text = text.replace('\\\\n', '\\n')  # 处理转义的换行符
            text = text.strip()  # 移除首尾空白
            
            # 处理长文本自动换行
            if len(text) > 20 and '\n' not in text:  # 如果单行文本超过20个字符且没有手动换行
                # 每20个字符左右自动换行
                lines = []
                current_line = []
                current_length = 0
                words = text.split()
                
                for word in words:
                    if current_length + len(word) > 20:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                    else:
                        current_line.append(word)
                        current_length += len(word) + 1  # +1 for space
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                text = '\n'.join(lines)
        else:
            text = ""
        
        if not identifier:
            await matcher.finish("请指定表情名称或ID")
        
        selected_sticker = resource_manager.select_sticker(identifier)
        if not selected_sticker:
            await matcher.finish("没有找到对应的表情")

        if not text:
            await matcher.finish("文本内容不能为空")

        # 处理命令行参数
        params = {}
        if args.size:
            try:
                params["font_size"] = int(args.size)
                logger.debug(f"设置字体大小: {params['font_size']}")
            except ValueError:
                await matcher.finish("字体大小必须是数字")
        
        if args.font_color:
            try:
                font_color = args.font_color if args.font_color.startswith('#') else f"#{args.font_color}"
                params["font_color"] = font_color
                # 自动生成更深的描边颜色
                # 将十六进制颜色转换为RGB，每个分量减少30%生成更深的颜色
                r = int(font_color[1:3], 16)
                g = int(font_color[3:5], 16)
                b = int(font_color[5:7], 16)
                r = max(0, int(r * 0.7))
                g = max(0, int(g * 0.7))
                b = max(0, int(b * 0.7))
                params["stroke_color"] = f"#{r:02x}{g:02x}{b:02x}"
            except ValueError:
                await matcher.finish("颜色格式错误，请使用十六进制颜色值")
        
        if args.x:
            try:
                params["x"] = int(args.x)
            except ValueError:
                await matcher.finish("x坐标必须是数字")
        
        if args.y:
            try:
                params["y"] = int(args.y)
            except ValueError:
                await matcher.finish("y坐标必须是数字")
        
        if args.rotate:
            try:
                params["rotate"] = float(args.rotate)
            except ValueError:
                await matcher.finish("旋转角度必须是数字")
        
        if args.stroke_width:
            try:
                params["stroke_width"] = int(args.stroke_width)
            except ValueError:
                await matcher.finish("描边宽度必须是数字")
        
        if args.stroke_color:
            if args.stroke_color.startswith("#"):
                params["stroke_color"] = args.stroke_color
            else:
                params["stroke_color"] = f"#{args.stroke_color}"

        # 从文中提取可能的参数（如果有的话）
        if "--size" in text or "--color" in text:
            parts = text.split("--")
            text = parts[0].strip()
            for part in parts[1:]:
                if part.startswith("size"):
                    try:
                        size_val = part.split()[1]
                        params["font_size"] = int(size_val)
                    except (IndexError, ValueError):
                        pass
                elif part.startswith("color"):
                    try:
                        color_val = part.split()[1]
                        params["font_color"] = f"#{color_val}" if not color_val.startswith("#") else color_val
                    except (IndexError, ValueError):
                        pass

        try:
            # 生成表情图片
            image = await generate_sticker_image(
                selected_sticker,
                text,
                auto_adjust=True,  # 默认启用自动调整
                **params
            )
            logger.debug(f"生成表情图片参数: {params}")
        except Exception as e:
            logger.exception("生成表情图片失败")
            await matcher.finish(f"生成表情图片失败: {str(e)}")

        # 发送图片
        if plugin_config.arcaea_reply:
            await matcher.finish(MessageSegment.image(image), at_sender=True)
        else:
            await matcher.finish(MessageSegment.image(image))

    except Exception as e:
        # 只记录错误，不显示详细信息
        logger.opt(exception=e).debug("处理出错")
        # 直接结束，不显示错误消息
        await matcher.finish()

# 以下是交互模式的处理器
@arc.handle()
async def handle_first_msg(matcher: Matcher, event: MessageEvent, state: T_State):
    """处理第一条消息"""
    # 显示角色列表
    try:
        image = await resource_manager.get_all_characters_grid()
        msg = (
            MessageSegment.image(image) + 
            "请发送你要生成表情的角色名称，或者直接发送表情 ID，或者发送 `随机` 使用一张随机表情\n"
            "Tip：你可以随时发送 `0` 退出交互模式"
        )
        if plugin_config.arcaea_reply:
            await matcher.send(msg, at_sender=True, reply_message=event.message_id)
        else:
            await matcher.send(msg)
    except Exception as e:
        await matcher.finish(f"获取角色列表出错:\n{e}")

@arc.got("character")
async def handle_character(matcher: Matcher, event: MessageEvent, state: T_State, arg: str = ArgPlainText("character")):
    """处理角色选择"""
    if arg in ("0", "q", "e", "quit", "exit", "退出"):
        await matcher.finish("已退出交互模式")
        
    # 选择表情
    sticker_info = resource_manager.select_sticker(arg)
    if not sticker_info:
        await matcher.reject("没有找到对应的表情,请重新输入")
        
    state["sticker_info"] = sticker_info
    msg = "请发送要添加的文字"
    if plugin_config.arcaea_reply:
        await matcher.send(msg, at_sender=True, reply_message=event.message_id)
    else:
        await matcher.send(msg)

@arc.got("text")
async def handle_text(
    matcher: Matcher,
    event: MessageEvent,
    state: T_State,
    text: str = ArgPlainText("text"),
):
    """处理文字输入"""
    sticker_info = state["sticker_info"]
    
    # 处理换行符
    text = text.replace("\\n", "\n")  # 处理显式的换行符
    text = text.strip()  # 移除首尾空白
    
    try:
        image = await generate_sticker_image(
            sticker_info,
            text,
            auto_adjust=True  # 只在交互模式下启用自动调整
        )
    except Exception as e:
        logger.exception("生成表情出错")
        await matcher.finish(f"生成表情出错: {e}")
        
    msg = MessageSegment.image(image)
    if plugin_config.arcaea_reply:
        await matcher.send(msg, at_sender=True, reply_message=event.message_id)
    else:
        await matcher.send(msg)
    await matcher.finish()

# 在插件加载时检查目录
@driver.on_startup
async def check_resources():
    """检查资源文件"""
    # 检查字体目录
    if not FONT_DIR.exists():
        logger.warning(f"字体目录不存在，创建目录: {FONT_DIR}")
        FONT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 检查图片目录
    if not RESOURCE_DIR.exists():
        logger.warning(f"图片目录不存在，创建目录: {RESOURCE_DIR}")
        RESOURCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 检查必要的文件
    required_files = [
        RESOURCE_DIR / "arcaea_stickers.png",
        FONT_DIR / "YurukaFangTang.ttf"
    ]
    
    for file in required_files:
        if not file.exists():
            logger.warning(f"缺少必要文件: {file}")