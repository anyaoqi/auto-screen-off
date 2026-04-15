"""
UI 样式常量
定义全局颜色、字体、间距等设计规范。
"""

# ============================================================
# 色彩方案
# ============================================================

# 主色调渐变（蓝紫色系）
PRIMARY_GRADIENT_START = "#667eea"
PRIMARY_GRADIENT_END = "#764ba2"

# 背景色
BG_COLOR = "#f5f7fa"  # 浅灰白
CARD_BG_COLOR = "#ffffff"  # 卡片背景（纯白）
DARK_BG_COLOR = "#1e1e1e"  # Toast背景

# 文字颜色
TEXT_PRIMARY = "#1a202c"  # 深灰（主文字）- 增强对比度
TEXT_SECONDARY = "#4a5568"  # 中灰（副标题）- 增强对比度
TEXT_WHITE = "#ffffff"  # 白色文字
TEXT_LIGHT = "#718096"  # 浅灰文字 - 增强对比度

# 按钮颜色
BTN_CONFIRM_START = "#4facfe"  # 确认按钮渐变蓝
BTN_CONFIRM_END = "#00f2fe"
BTN_CONFIRM = "#4facfe"  # 确认按钮单色
BTN_CANCEL = "#e2e8f0"  # 取消按钮浅灰
BTN_CANCEL_TEXT = "#4a5568"  # 取消按钮文字
BTN_DANGER = "#f56565"  # 警告/退出按钮
BTN_SUCCESS = "#48bb78"  # 成功按钮

# 卡片/元素强调色
ACCENT_BLUE = "#4facfe"
ACCENT_PURPLE = "#667eea"
ACCENT_GREEN = "#48bb78"
ACCENT_ORANGE = "#ed8936"
ACCENT_RED = "#f56565"

# 阴影和分隔线
SHADOW_COLOR = "#e2e8f0"
DIVIDER_COLOR = "#edf2f7"

# ============================================================
# 字体规范
# ============================================================

FONT_FAMILY = "Microsoft YaHei UI"
FONT_FAMILY_NUM = "Segoe UI"

FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 16, "bold")
FONT_BODY = (FONT_FAMILY, 14)
FONT_BODY_BOLD = (FONT_FAMILY, 14, "bold")
FONT_SMALL = (FONT_FAMILY, 12)
FONT_TINY = (FONT_FAMILY, 11)
FONT_BUTTON = (FONT_FAMILY, 13, "bold")
FONT_BUTTON_SM = (FONT_FAMILY, 12)

# 数字专用字体
FONT_NUM_LARGE = (FONT_FAMILY_NUM, 36, "bold")
FONT_NUM_MEDIUM = (FONT_FAMILY_NUM, 24)
FONT_NUM_SMALL = (FONT_FAMILY_NUM, 18)

# ============================================================
# 间距规范
# ============================================================

PADDING_CARD = 20  # 卡片内边距
PADDING_ELEMENT = 12  # 元素间距
PADDING_BTN = (10, 24)  # 按钮内边距 (y, x)

RADIUS_WINDOW = 12  # 窗口圆角
RADIUS_BUTTON = 10  # 按钮圆角
RADIUS_CARD = 16  # 卡片圆角
RADIUS_TOAST = 16  # Toast圆角

# ============================================================
# Toast 通知参数
# ============================================================

TOAST_WIDTH = 380
TOAST_HEIGHT = 190
TOAST_MARGIN = 20  # 距屏幕边缘
TOAST_BG = "rgba(30, 30, 30, 0.95)"
TOAST_ANIM_DURATION = 300  # 动画时长（ms）

# ============================================================
# 设置窗口参数
# ============================================================

SETTINGS_WIDTH = 540
SETTINGS_HEIGHT = 660

# ============================================================
# 滑块参数范围
# ============================================================

IDLE_TIMEOUT_MIN = 5
IDLE_TIMEOUT_MAX = 60
IDLE_TIMEOUT_DEFAULT = 10

COUNTDOWN_MIN = 10
COUNTDOWN_MAX = 60
COUNTDOWN_DEFAULT = 30
