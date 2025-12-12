import platform

import psutil


def get_python_version() -> str:
    return {
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "compiler": platform.python_compiler(),
    }


def get_memory_stats() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / 1024**3, 2),
        "used_gb": round(mem.used / 1024**3, 2),
        "percent": mem.percent,
    }


def get_cpu_stats() -> dict:
    load = [round(x, 2) for x in psutil.getloadavg()]
    return {
        "usage_percent": psutil.cpu_percent(interval=0.2),
        "load_avg": load,
    }
