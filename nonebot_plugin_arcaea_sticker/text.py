import math
from typing import List

class TextSizeCalculator:
    """计算文字大小"""
    def __init__(self, max_width: int, max_height: int):
        """初始化计算器的最大宽高"""
        self.max_width = max_width
        self.max_height = max_height
    
    def calc_char_width(self, char: str, size: int) -> float:
        """计算单个字符宽度,中文字符宽度为size,英文为0.6倍"""
        return size if len(char.encode('utf-8')) > 1 else size * 0.6
    
    def calc_line_width(self, line: str, size: int, rotate_deg: float) -> float:
        """计算单行文本宽度,考虑旋转角度"""
        char_widths = sum(self.calc_char_width(c, size) for c in line)
        rotate_rad = math.radians(rotate_deg)
        return abs(char_widths * math.cos(rotate_rad)) + abs(size * math.sin(rotate_rad))
    
    def calc_text_size(self, text: str, base_size: int, rotate_deg: float) -> int:
        """计算最适合的文字大小"""
        lines = text.split('\n')
        text_length = len(text)
        
        # 基于文本长度的动态缩放
        scale_factor = self._get_scale_factor(text_length)
        initial_size = self._calc_initial_size(lines, base_size, scale_factor)
        
        return self._adjust_size(lines, initial_size, rotate_deg)
    
    def _get_scale_factor(self, text_length: int) -> float:
        """获取文本长度的缩放因子"""
        if text_length <= 4:
            return 1.2
        elif text_length <= 8:
            return 1.0
        elif text_length <= 12:
            return 0.9
        return 0.8
    
    def _calc_initial_size(self, lines: List[str], base_size: int, scale_factor: float) -> int:
        """计算初始字体大小"""
        max_line_length = max(len(line) for line in lines)
        num_lines = len(lines)
        
        width_based = min(base_size, self.max_width * scale_factor / (max_line_length * 0.8))
        height_based = min(base_size, self.max_height * scale_factor / (num_lines * 1.2))
        
        return int(min(width_based, height_based))
    
    def _adjust_size(self, lines: List[str], size: int, rotate_deg: float) -> int:
        """调整字体大小直到合适"""
        while size > 20:
            max_width = max(
                self.calc_line_width(line, size, rotate_deg)
                for line in lines
            )
            total_height = len(lines) * size * 1.2
            
            if max_width <= self.max_width * 0.85 and total_height <= self.max_height * 0.8:
                break
            size -= 1
        
        return min(max(size, 20), 45)