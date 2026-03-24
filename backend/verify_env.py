"""
环境验证脚本
检查所有依赖是否正确安装
"""
import sys
import importlib
from typing import List, Tuple


REQUIRED_PACKAGES = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("numpy", "NumPy"),
    ("scipy", "SciPy"),
    ("pydub", "Pydub"),
    ("celery", "Celery"),
    ("redis", "Redis"),
    ("sqlalchemy", "SQLAlchemy"),
    ("aiosqlite", "AIOSQLite"),
    ("torch", "PyTorch"),
    ("torchaudio", "TorchAudio"),
]


def check_package(name: str, display_name: str) -> Tuple[bool, str]:
    """检查单个包是否安装"""
    try:
        module = importlib.import_module(name)
        version = getattr(module, "__version__", "unknown")
        return True, f"{display_name} v{version}"
    except ImportError as e:
        return False, f"{display_name} 未安装：{e}"


def check_python_version() -> Tuple[bool, str]:
    """检查 Python 版本"""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 10:
        return True, f"Python {version_str}"
    else:
        return False, f"Python {version_str} (需要 3.10+)"


def check_ffmpeg() -> Tuple[bool, str]:
    """检查 FFmpeg 是否安装"""
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split("\n")[0]
            return True, version_line
        else:
            return False, "FFmpeg 未正确安装"
    except FileNotFoundError:
        return False, "FFmpeg 未安装"
    except Exception as e:
        return False, f"FFmpeg 检查失败：{e}"


def main():
    """主验证函数"""
    print("="*60)
    print("MelodyClaw 环境验证")
    print("="*60)
    print()
    
    all_passed = True
    
    # 检查 Python 版本
    print("📋 系统检查")
    print("-"*40)
    passed, msg = check_python_version()
    status = "✅" if passed else "❌"
    print(f"  {status} {msg}")
    all_passed = all_passed and passed
    print()
    
    # 检查 FFmpeg
    passed, msg = check_ffmpeg()
    status = "✅" if passed else "❌"
    print(f"  {status} {msg}")
    all_passed = all_passed and passed
    print()
    
    # 检查 Python 包
    print("📦 Python 依赖检查")
    print("-"*40)
    for pkg_name, display_name in REQUIRED_PACKAGES:
        passed, msg = check_package(pkg_name, display_name)
        status = "✅" if passed else "❌"
        print(f"  {status} {msg}")
        all_passed = all_passed and passed
    print()
    
    # 检查目录结构
    print("📁 目录结构检查")
    print("-"*40)
    from pathlib import Path
    base_dir = Path(__file__).parent.parent
    required_dirs = [
        "backend/app",
        "backend/app/models",
        "backend/app/api/v1",
        "backend/app/services",
        "backend/app/tasks",
        "ai_models",
        "storage/uploads",
        "storage/processed",
        "storage/cache",
        "tests"
    ]
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        passed = full_path.exists() and full_path.is_dir()
        status = "✅" if passed else "❌"
        print(f"  {status} {dir_path}")
        all_passed = all_passed and passed
    print()
    
    # 总结
    print("="*60)
    if all_passed:
        print("✅ 所有检查通过！环境配置正确。")
        return 0
    else:
        print("❌ 部分检查失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
