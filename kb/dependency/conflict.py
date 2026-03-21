"""知识库依赖冲突检测器。"""

from collections import defaultdict
from typing import List
from kb.core.models import Dependency
from kb.exceptions import DependencyConflictError


class ConflictDetector:
    """依赖冲突检测器"""

    def check_conflicts(self, dependencies: List[Dependency]) -> None:
        """
        检查依赖版本冲突

        Args:
            dependencies: 依赖列表

        Raises:
            DependencyConflictError: 当检测到冲突时抛出
        """
        # 按知识库名称分组
        dependency_groups = defaultdict(list)
        for dep in dependencies:
            dependency_groups[dep.name].append(dep)

        conflicts = []

        # 检查每个知识库的版本冲突
        for name, deps in dependency_groups.items():
            if len(deps) > 1:
                # 获取所有版本号
                versions = [dep.version for dep in deps]

                # 检查是否有重复版本（相同版本不冲突）
                unique_versions = set(versions)
                if len(unique_versions) == 1:
                    # 所有版本相同，无冲突
                    continue

                # 存在冲突
                conflict_info = {
                    'name': name,
                    'versions': versions,
                    'unique_versions': list(unique_versions)
                }
                conflicts.append(conflict_info)

        if conflicts:
            # 生成冲突报告
            report = self._generate_conflict_report(conflicts)
            raise DependencyConflictError(report)

    def _generate_conflict_report(self, conflicts: List[dict]) -> str:
        """
        生成冲突报告

        Args:
            conflicts: 冲突信息列表

        Returns:
            冲突报告字符串
        """
        report_lines = ["检测到依赖版本冲突："]

        for i, conflict in enumerate(conflicts, 1):
            name = conflict['name']
            versions = conflict['versions']
            unique_versions = conflict['unique_versions']

            report_lines.append(f"\n{i}. 知识库 '{name}'")
            report_lines.append(f"   - 总请求数: {len(versions)}")
            report_lines.append(f"   - 版本列表: {', '.join(versions)}")
            report_lines.append(f"   - 冲突版本: {', '.join(unique_versions)}")
            report_lines.append("   - 冲突原因: 同一知识库有多个不同版本")

        report_lines.append(f"\n共发现 {len(conflicts)} 个冲突。")

        return '\n'.join(report_lines)