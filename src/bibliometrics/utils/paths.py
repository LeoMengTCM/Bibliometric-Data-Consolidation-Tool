from pathlib import Path
from typing import Optional, Union


PathLike = Union[str, Path]


def get_project_root() -> Path:
    """返回项目根目录。"""
    return Path(__file__).resolve().parents[3]


def resolve_project_path(path: PathLike) -> Path:
    """将相对路径解析为项目根目录下的绝对路径。"""
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj
    return get_project_root() / path_obj


def find_existing_analysis_file(
    data_dir: PathLike,
    preferred_file: Optional[PathLike] = None,
) -> Optional[Path]:
    """查找当前可用于分析/绘图的最终数据文件。"""
    base_dir = Path(data_dir)
    candidates = []

    if preferred_file:
        preferred_path = Path(preferred_file)
        if not preferred_path.is_absolute():
            preferred_path = base_dir / preferred_path
        candidates.append(preferred_path)

    candidates.append(base_dir / 'Final_Version.txt')
    candidates.extend(
        sorted(
            path for path in base_dir.glob('*_only.txt')
            if path.is_file() and not path.name.startswith('._') and not path.name.startswith('.')
        )
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None
