#!/usr/bin/env python3
"""
AISTEC Knowledge Graph 查询工具
Usage: 
  python tools/query.py prerequisites PHYS-NEWTON-001 --depth 2
  python tools/query.py path SCI-MOT-001 PHYS-NEWTON-001
  python tools/query.py grade 初中八年级
"""

import yaml
import argparse
from pathlib import Path
from collections import deque

class KnowledgeGraph:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.nodes = {}
        self.edges = []
        self._load_all()
    
    def _load_yaml(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except:
            return None
    
    def _load_all(self):
        # 加载所有知识点
        subjects_path = self.base_path / 'subjects'
        for yaml_file in subjects_path.rglob('*.yaml'):
            node = self._load_yaml(yaml_file)
            if node and 'id' in node:
                self.nodes[node['id']] = node
        
        # 加载所有关系
        relations_path = self.base_path / 'relations'
        if relations_path.exists():
            for rel_file in relations_path.rglob('*.yaml'):
                rel_data = self._load_yaml(rel_file)
                if rel_data and 'edges' in rel_data:
                    self.edges.extend(rel_data['edges'])
    
    def get_prerequisites(self, node_id, depth=1):
        """获取前置知识（支持多层）"""
        result = []
        visited = set()
        queue = deque([(node_id, 0)])
        
        while queue:
            current_id, current_depth = queue.popleft()
            if current_id in visited or current_depth > depth:
                continue
            visited.add(current_id)
            
            if current_id != node_id:
                node = self.nodes.get(current_id)
                if node:
                    result.append({
                        'id': current_id,
                        'name': node.get('name', 'Unknown'),
                        'depth': current_depth,
                        'required': True  # 简化处理
                    })
            
            # 查找前置关系
            for edge in self.edges:
                if edge.get('to') == current_id and edge.get('type') == 'prerequisite':
                    queue.append((edge.get('from'), current_depth + 1))
        
        return result
    
    def find_path(self, start_id, end_id):
        """查找从 start 到 end 的学习路径（BFS）"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return None
        
        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        
        while queue:
            current, path = queue.popleft()
            if current == end_id:
                return [self.nodes[nid]['name'] for nid in path if nid in self.nodes]
            
            # 查找后续知识
            for edge in self.edges:
                if edge.get('from') == current and edge.get('type') == 'prerequisite':
                    next_id = edge.get('to')
                    if next_id not in visited:
                        visited.add(next_id)
                        queue.append((next_id, path + [next_id]))
        
        return None
    
    def get_grade_concepts(self, grade_name):
        """获取指定年级的所有知识点"""
        result = []
        for node_id, node in self.nodes.items():
            if node.get('grade') == grade_name:
                result.append({
                    'id': node_id,
                    'name': node.get('name'),
                    'domain': node.get('domain', '')
                })
        return result

def main():
    parser = argparse.ArgumentParser(description='AISTEC Knowledge Graph Query Tool')
    parser.add_argument('command', choices=['prerequisites', 'path', 'grade'])
    parser.add_argument('target')
    parser.add_argument('--depth', type=int, default=1, help='查询深度（仅用于prerequisites）')
    parser.add_argument('--end', help='终点ID（仅用于path）')
    
    args = parser.parse_args()
    
    # 自动查找知识图谱根目录
    script_path = Path(__file__).parent
    kg_path = script_path.parent
    
    kg = KnowledgeGraph(kg_path)
    
    if args.command == 'prerequisites':
        prereqs = kg.get_prerequisites(args.target, args.depth)
        if not prereqs:
            print(f"⚠️  {args.target} 没有前置知识或不存在")
            return
        
        print(f"📚 {args.target} 的前置知识（深度={args.depth}）：")
        for p in prereqs:
            indent = "  " * p['depth']
            print(f"{indent}- {p['name']} ({p['id']})")
    
    elif args.command == 'path':
        if not args.end:
            print("❌ 使用 path 命令需要 --end 参数")
            return
        
        path = kg.find_path(args.target, args.end)
        if path:
            print(f"🛤️  从 {args.target} 到 {args.end} 的学习路径：")
            print(" → ".join(path))
        else:
            print(f"❌ 未找到从 {args.target} 到 {args.end} 的路径")
    
    elif args.command == 'grade':
        concepts = kg.get_grade_concepts(args.target)
        if not concepts:
            print(f"⚠️  没有找到 {args.target} 的知识点")
            return
        
        print(f"📖 {args.target} 的知识点（共 {len(concepts)} 个）：")
        for c in concepts:
            print(f"  - {c['name']} ({c['id']})")

if __name__ == '__main__':
    main()
