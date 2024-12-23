<div align="center">

# Arcaea 表情包生成器

_✨ 基于 NoneBot2 的 Arcaea 表情包生成插件 ✨_

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
  <a href="https://pypi.python.org/pypi/nonebot-plugin-arcaea-sticker">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-arcaea-sticker.svg" alt="pypi">
  </a>
</p>

<p align="center">
  <a href="https://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=sy5x0Bv8IJoMVviC3dRbXTVD9zLdpitx&authKey=OPfY0G2zfQwDQJmf5xV5cqJq7c6%2Beg1cqiCF%2BDHsSFEaGscmeo5ALIdyJ%2BYZmoJb&noverify=0&group_code=806446119">
    <img src="https://img.shields.io/badge/QQ群-806446119-pink" alt="QQ Chat Group">
  </a>
  <a href="https://pydantic.dev">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/pyd-v1-or-v2.json" alt="Pydantic Version 1 Or 2" >
  </a>
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Agnes4m/nonebot_plugin_pjsk.svg" alt="license">
  </a>
</p>


<p align="center">
  <img src="https://github.com/JQ-28/nonebot-plugin-arcaea-sticker/blob/main/nami%E9%BE%99%E7%AC%94!%E9%BE%99%E7%AC%94!.png" alt="示例图片">
</p>

</div>

## 📖 介绍

本插件可以生成 Arcaea 风格的表情包，支持自定义文字、位置、角度、颜色等参数。

## 💿 安装

### 方式一：使用 nb-cli 安装（推荐）

```bash
nb plugin install nonebot-plugin-arcaea-sticker
```

### 方式二：使用包管理器安装

1. 使用 pip 安装插件：
```bash
pip install nonebot-plugin-arcaea-sticker
```

2. 在 NoneBot2 项目的 `pyproject.toml` 文件中添加插件：
```toml
[tool.nonebot]
plugins = ["nonebot_plugin_arcaea_sticker"]
```

## ⚙️ 配置

在 NoneBot2 项目的 `.env` 文件中添加以下配置：

```env
# 是否回复消息
arcaea_reply=true
```

## 🎮 使用方法

### 基础指令
- `arc <角色> <文字>` - 生成表情包
- `arc -h` - 显示帮助
- `arc` - 进入交互模式

### 自定义参数（都是可选的）
| 参数 | 说明 | 范围 | 默认值 | 补充说明 |
|------|------|------|--------|----------|
| `-s, --size` | 文字大小 | 20~45 | 35 | 数字越大文字越大,多行文字建议25-35 |
| `-x` | 横向位置 | 0~296 | 148 | 0=最左边,148=居中,296=最右边 |
| `-y` | 纵向位置 | 0~256 | 128 | 0=最上方,128=居中,256=最下方 |
| `-r, --rotate` | 旋转角度 | -180~180 | -12 | 正数顺时针,负数逆时针,建议-30~30度 |
| `-c, --color` | 文字颜色 | 十六进制 | 角色专属 | 支持`#ff0000`或`ff0000`格式 |
| `-w, --stroke-width` | 描边宽度 | 整数 | 9 | 文字边框的粗细 |
| `-C, --stroke-color` | 描边颜色 | 十六进制 | 自动生成 | 默认比文字颜色深30% |

💡 提示: 文字包含空格需要加引号,换行使用`\n`

### 使用示例
```
arc luna 好耶！                         # 基础用法
arc hikari "第一行\n第二行" -s 45         # 多行文字
arc 17 喜欢... -x 150 -y 100 -r -20    # 调整位置和角度
arc nami "龙笔!" -c ff0000              # 自定义红色文字
arc eto "Ciallo～(∠・ω<)⌒☆" -s 30 -c #fdae92 -r -28 -x 120 -y 80  # 组合多个参数
```

## 📝 功能特点

- ✅ 支持生成 Arcaea 角色的表情包
- ✅ 支持命令模式和交互模式
- ✅ 支持自定义文字、位置、角度、颜色等参数
- ✅ 支持多行文本和自动换行
- ✅ 智能文字大小调整
- ✅ 支持中文角色名称

## 🔧 依赖

- Python
- NoneBot2 
- nonebot-adapter-onebot
- nonebot-plugin-htmlrender 
- nonebot-plugin-localstore 
- Playwright

## 📄 开源许可

本项目基于 [MIT](LICENSE) 许可证开源。

**注意事项：**
- 本项目代码使用 MIT 许可证开源，您可以自由使用和修改代码
- 项目中的表情包素材来源于 [Xestarrrr](https://x.com/Xestarrrr)
- 本项目基于 [arcaea-stickers](https://github.com/Rosemoe/arcaea-stickers) 项目开发
- 请遵守原始素材的使用条款和限制

## 🙏 鸣谢

- [Xestarrrr](https://x.com/Xestarrrr) - 原始表情包素材创作者
- [arcaea-stickers](https://github.com/Rosemoe/arcaea-stickers) - 网页版表情包生成器
- [nonebot-plugin-pjsk](https://github.com/lgc-NB2Dev/nonebot-plugin-pjsk) - 参考了部分代码
- [NoneBot2](https://github.com/nonebot/nonebot2) - 跨平台 Python 异步机器人框架

## 📞 联系

<table>
  <tr>
    <td>ღ互联网小猫窝ღ(Bot群,欢迎来玩)</td>
    <td>JQ-28</td>
  </tr>
  <tr>
    <td>QQ群：806446119</td>
    <td>QQ：480352716</td>
  </tr>
</table>

</div>

第一次写代码，比较史，请见谅，如有问题或建议请直接发issue，我会尽量解决