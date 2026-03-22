from pathlib import Path

def find_knowledge_file(current_dir: Path, src_path: Path = None) -> Path:
    """查找知识库文件，优先在src目录下查找，如果未找到则向上搜索 Knowledge.md"""
    current = Path(current_dir).resolve()

    # 如果指定了src目录，先在src目录下查找
    if src_path is None:
        src_path = current / "src"

    # 优先在src目录下查找
    if src_path.exists() and src_path.is_dir():
        knowledge_file = src_path / "Knowledge.md"
        if knowledge_file.exists() and knowledge_file.is_file():
            return knowledge_file

    # 如果src目录下未找到，从当前目录向上搜索最多5层
    for _ in range(5):
        knowledge_file = current / "Knowledge.md"
        if knowledge_file.exists() and knowledge_file.is_file():
            return knowledge_file
        parent = current.parent
        if parent == current:  # 到达根目录
            break
        current = parent

    raise FileNotFoundError("未找到 Knowledge.md 文件")
