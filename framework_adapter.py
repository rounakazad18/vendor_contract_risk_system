"""
Microsoft Semantic Kernel & Agent Framework Integration Adapter (`framework_adapter.py`).
"""

from __future__ import annotations
import functools
from typing import Any, Callable, Dict, List, Optional

try:
    from semantic_kernel import Kernel as _SKKernel  # type: ignore
    from semantic_kernel.functions import kernel_function as _sk_kernel_function  # type: ignore
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    _SKKernel = None
    _sk_kernel_function = None
    SEMANTIC_KERNEL_AVAILABLE = False


def kernel_function(name: Optional[str] = None, description: Optional[str] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        tool_desc = description or (func.__doc__ or "").strip()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        setattr(wrapper, "__kernel_function__", True)
        setattr(wrapper, "__kernel_function_name__", tool_name)
        setattr(wrapper, "__kernel_function_description__", tool_desc)
        return wrapper

    return decorator


class AgentKernelRegistry:
    def __init__(self) -> None:
        self.plugins: Dict[str, Dict[str, Callable]] = {}
        self.tool_metadata: List[Dict[str, str]] = []
        self._native_kernel = _SKKernel() if (SEMANTIC_KERNEL_AVAILABLE and _SKKernel) else None

    def register_plugin(self, plugin_instance: object, plugin_name: str) -> None:
        self.plugins[plugin_name] = {}
        for attr_name in dir(plugin_instance):
            if attr_name.startswith("_"):
                continue
            member = getattr(plugin_instance, attr_name)
            if callable(member) and getattr(member, "__kernel_function__", False):
                fn_name = getattr(member, "__kernel_function_name__", attr_name)
                fn_desc = getattr(member, "__kernel_function_description__", "")
                self.plugins[plugin_name][fn_name] = member
                self.tool_metadata.append(
                    {
                        "plugin": plugin_name,
                        "function": fn_name,
                        "description": fn_desc,
                    }
                )
