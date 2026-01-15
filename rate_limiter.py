#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API速率限制器

防止429错误（Too Many Requests）的全局速率限制器。

作者：Meng Linghan
开发工具：Claude Code
日期：2025-11-20
版本：v1.0
"""

import time
import threading
from typing import Optional


class RateLimiter:
    """
    API速率限制器

    使用令牌桶算法实现速率限制，确保API调用不超过限制。
    线程安全设计，支持多线程并发使用。
    """

    def __init__(self, requests_per_minute: int = 30, min_interval: float = 1.5):
        """
        初始化速率限制器

        Args:
            requests_per_minute: 每分钟最大请求数（默认30，保守值）
            min_interval: 最小请求间隔（秒，默认1.5秒）
        """
        self.requests_per_minute = requests_per_minute
        self.min_interval = min_interval
        self.last_request_time = 0
        self.lock = threading.Lock()

    def acquire(self):
        """
        获取API调用许可（阻塞直到可以发送请求）

        使用令牌桶算法：
        1. 确保与上次请求间隔至少min_interval秒
        2. 线程安全，多线程环境下正确工作
        """
        with self.lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time

            # 如果距离上次请求时间太短，等待
            if time_since_last_request < self.min_interval:
                wait_time = self.min_interval - time_since_last_request
                time.sleep(wait_time)

            # 更新上次请求时间
            self.last_request_time = time.time()

    def wait_for_quota(self, seconds: int = 60):
        """
        等待配额恢复（用于处理429错误后的恢复）

        Args:
            seconds: 等待秒数（默认60秒）
        """
        time.sleep(seconds)


# 全局单例实例
_global_rate_limiter: Optional[RateLimiter] = None


def get_global_rate_limiter() -> RateLimiter:
    """
    获取全局速率限制器实例（单例模式）

    Returns:
        全局RateLimiter实例
    """
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter(
            requests_per_minute=30,  # 每分钟30个请求
            min_interval=1.5         # 最小间隔1.5秒
        )
    return _global_rate_limiter


def reset_global_rate_limiter(requests_per_minute: int = 30, min_interval: float = 1.5):
    """
    重置全局速率限制器（用于测试或调整参数）

    Args:
        requests_per_minute: 每分钟最大请求数
        min_interval: 最小请求间隔（秒）
    """
    global _global_rate_limiter
    _global_rate_limiter = RateLimiter(
        requests_per_minute=requests_per_minute,
        min_interval=min_interval
    )


if __name__ == '__main__':
    # 测试速率限制器
    print("=" * 80)
    print("速率限制器测试")
    print("=" * 80)
    print()

    limiter = RateLimiter(requests_per_minute=30, min_interval=1.5)

    print("测试连续5次请求（应该每次间隔1.5秒）...")
    for i in range(5):
        start_time = time.time()
        limiter.acquire()
        elapsed = time.time() - start_time
        print(f"请求 {i+1}: 等待了 {elapsed:.2f} 秒")

    print()
    print("✓ 测试完成")
    print("=" * 80)
