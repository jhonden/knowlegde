from pathlib import Path

def find_knowledge_file(current_dir: Path, src_path: Path = None) -> Path:
    """查找知识库文件，优先在src目录下查找，如果未找到则向上搜索 Knowledge.md

    当前实现问题：当src_path存在且是目录时，会检查 src_path + "Knowledge.md" 是否存在，
    而不是检查这个路径本身是否真的是目录

    Args:
        current_dir: 当前工作目录
        src_path: 可选的src目录路径

    Returns:
        Path: 知识库文件的绝对路径
    """
    current = Path(current_dir).resolve()

    # 如果指定了src目录，先在src目录下查找
    if src_path is None:
        src_path = current / "src"
    # 检查src_path是否是目录（只有当它是目录时才在src下查找）
        if src_path.exists() and src_path.is_dir():
            knowledge_file = src_path / "Knowledge.md"
            if knowledge_file.exists() and knowledge_file.is_file():
                return knowledge_file
        # 如果src目录不存在，或者不是目录，从当前目录向上搜索 DEFAULT_KNOWLEDGE_FILE
        return (Path.cwd() / "Knowledge.md").resolve()
    else:
        return Path(path).resolve()
