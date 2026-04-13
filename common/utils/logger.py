import ctypes
import logging
import os
import sys
import time
from typing import Optional

# ── Windows 下启用 ANSI 转义码 ─────────────────────────────
if sys.platform == "win32":
    kernel32 = ctypes.windll.kernel32
    # STD_OUTPUT_HANDLE = -11
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    kernel32.SetConsoleMode(handle, mode.value | 0x0004)

# ── ANSI 颜色 ──────────────────────────────────────────────
_LEVEL_COLORS = {
    logging.DEBUG:    "\033[36m",   # 青色
    logging.INFO:     "\033[32m",   # 绿色
    logging.WARNING:  "\033[33m",   # 黄色
    logging.ERROR:    "\033[31m",   # 红色
    logging.CRITICAL: "\033[35m",   # 紫色
}
_RESET = "\033[0m"

# ── 格式：时间 │ 级别(颜色) │ 模块:行号 │ 消息 ────────────
_FMT = "%(asctime)s │ %(colored_levelname)-8s │ %(short_path)s:%(lineno)d │ %(message)s"


class _ColorFormatter(logging.Formatter):
    """带颜色和结构的日志格式器"""

    def __init__(self):
        super().__init__(fmt=_FMT)

    def format(self, record: logging.LogRecord) -> str:
        # 注入彩色级别名
        color = _LEVEL_COLORS.get(record.levelno, "")
        record.colored_levelname = f"{color}{record.levelname}{_RESET}"
        # 缩短路径：只保留相对于项目根目录的路径
        record.short_path = _shorten_path(record.pathname)
        # 格式化消息（支持任意对象 repr）
        record.msg = _safe_repr(record.msg, record.args)
        record.args = ()  # 已手动格式化，不再让 Formatter 重复处理
        return super().format(record)

    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        ct = time.localtime(record.created)
        return time.strftime("%Y-%m-%d %H:%M:%S", ct) + f".{int(record.msecs):03d}"


def _shorten_path(pathname: str) -> str:
    """将绝对路径缩短为相对路径，只保留关键部分"""
    # 尝试相对化到 cwd
    try:
        rel = os.path.relpath(pathname)
    except ValueError:
        return pathname
    # 去掉开头的 .\ 或 ..\ 前缀
    parts = rel.replace("\\", "/").split("/")
    # 取最后两段（如 core/redis/client.py）
    if len(parts) > 2:
        return "/".join(parts[-2:])
    return rel


def _safe_repr(msg, args) -> str:
    """将消息和参数安全转为可读字符串"""
    if not isinstance(msg, str):
        msg = repr(msg)
    if args:
        try:
            msg = msg % args
        except (TypeError, ValueError):
            msg = f"{msg} | args={args!r}"
    return msg


# ── 全局 handler（只创建一次）──────────────────────────────
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(_ColorFormatter())

_configured_loggers: set[str] = set()


def _ensure_handler(logger: logging.Logger):
    """保证 handler 只挂一次，避免重复输出"""
    if logger.name not in _configured_loggers:
        logger.addHandler(_handler)
        _configured_loggers.add(logger.name)


# ── 公开 API ───────────────────────────────────────────────

def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """创建带颜色和格式化的 Logger

    用法:
        logger = get_logger("my_module")
        logger.info("服务启动")
        logger.debug("对象详情: %s", some_obj)
        logger.error("出错了", exc_info=True)       # 自动打印异常堆栈
        logger.warning("可疑", stack_info=True)      # 打印调用堆栈
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    _ensure_handler(logger)
    return logger


# 便捷别名，满足 logger = Logger(name="模块名") 风格
Logger = get_logger
