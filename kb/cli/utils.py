from pathlib import Path

def find_knowledge_file(current_dir: Path) -> Path:
    """查找知识库文件，从当前目录向上搜索 Knowledge.md"""
    current = Path(current_dir).resolve()

    # 从当前目录向上搜索最多5层
    for _ in range(5):
        knowledge_file = current / "Knowledge.md"
        if knowledge_file.exists() and knowledge_file.is_file():
            return knowledge_file

        parent = current.parent
        if parent == current:  # 到达根目录
            break
        current = parent

    raise FileNotFoundError("未找到 Knowledge.md 文件")