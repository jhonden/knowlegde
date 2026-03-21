"""Update command implementation for kb CLI."""

import click
from pathlib import Path
from typing import Optional

from kb.cli.utils import find_knowledge_file
from kb.update.checker import VersionChecker
from kb.update.updater import DependencyUpdater
from kb.core.parser import KnowledgeParser
from kb.exceptions import KnowledgeBaseError


@click.command()
@click.option(
    "--path",
    type=click.Path(exists=False),
    default=None,
    help="知识库文件路径"
)
def check_updates(path: Optional[str]):
    """检查依赖是否有新版本"""
    if path:
        knowledge_file = Path(path)
    else:
        knowledge_file = find_knowledge_file()

    if not knowledge_file or not knowledge_file.exists():
        click.echo("未找到知识库文件")
        return

    try:
        checker = VersionChecker()
        parser = KnowledgeParser()
        metadata = parser.parse(knowledge_file)

        if not metadata.dependencies:
            click.echo("无依赖需要检查")
            return

        updates = checker.check_updates(metadata.dependencies)

        if not updates:
            click.echo("所有依赖都是最新版本")
            return

        click.echo(f"发现 {len(updates)} 个可用更新:")
        for update in updates:
            click.echo(
                f"  {update.name}: "
                f"{update.current_version} → {update.latest_version}"
            )

    except KnowledgeBaseError as e:
        click.echo(f"错误: {e}")
    except Exception as e:
        click.echo(f"错误: {e}")


@click.command()
@click.argument("name", required=False)
@click.option(
    "--path",
    type=click.Path(exists=False),
    default=None,
    help="知识库文件路径"
)
def update(name: Optional[str], path: Optional[str]):
    """更新依赖到新版本

    如果不指定 NAME，则更新所有可更新的依赖。
    """
    if path:
        knowledge_file = Path(path)
    else:
        knowledge_file = find_knowledge_file()

    if not knowledge_file or not knowledge_file.exists():
        click.echo("未找到知识库文件")
        return

    try:
        checker = VersionChecker()
        parser = KnowledgeParser()
        updater = DependencyUpdater()

        if not name:
            # 更新所有依赖
            metadata = parser.parse(knowledge_file)

            if not metadata.dependencies:
                click.echo("无依赖需要更新")
                return

            updates = checker.check_updates(metadata.dependencies)

            if not updates:
                click.echo("所有依赖都是最新版本")
                return

            click.echo(f"发现 {len(updates)} 个可用更新:")
            for update in updates:
                click.echo(
                    f"  {update.name}: "
                    f"{update.current_version} → {update.latest_version}"
                )

            if not click.confirm("确认更新以上依赖？"):
                click.echo("取消更新")
                return

            # 逐个更新
            update_dict = {}
            for update in updates:
                updater.update_dependency(
                    knowledge_file,
                    update.name,
                    update.latest_version
                )
                update_dict[update.name] = update.latest_version
                click.echo(f"  {update.name} 已更新到 {update.latest_version}")

            click.echo("更新完成")

        else:
            # 更新指定依赖
            metadata = parser.parse(knowledge_file)

            # 查找依赖
            target_dep = None
            for dep in metadata.dependencies:
                if dep.name == name:
                    target_dep = dep
                    break

            if not target_dep:
                click.echo(f"错误: 未找到依赖 '{name}'")
                return

            # 检查更新
            update_list = checker.check_single_dependency(knowledge_file, name)

            if not update_list.has_updates():
                click.echo(f"{name} 已经是最新版本 ({target_dep.version})")
                return

            update = update_list.updates[0]
            click.echo(
                f"{name}: {update.current_version} → {update.latest_version}"
            )

            if not click.confirm("确认更新？"):
                click.echo("取消更新")
                return

            # 更新依赖
            updater.update_dependency(
                knowledge_file,
                name,
                update.latest_version
            )

            click.echo(f"{name} 已更新到 {update.latest_version}")

    except KnowledgeBaseError as e:
        click.echo(f"错误: {e}")
    except Exception as e:
        click.echo(f"错误: {e}")
