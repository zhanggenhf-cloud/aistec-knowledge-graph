#!/usr/bin/env python3
"""
AISTEC Knowledge Graph 数据校验工具
Usage: python tools/validate.py
"""

import yaml
import os
import sys
from pathlib import Path

def load_yaml(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        return {"_error": str(e)}

def validate_node(node, filepath):
    """校验单个知识点节点"""
    errors = []
    
    # 必需字段
    required_fields = ['id', 'name', 'subject', 'grade']
    for field in required_fields:
        if field not in node or not node[field]:
            errors.append(f"[{filepath}] 缺少必需字段: {field}")
    
    # ID 格式检查
    if 'id' in node:
        parts = node['id'].split('-')
        if len(parts) != 3:
            errors.append(f"[{filepath}] ID 格式错误: {node['id']} (应为 SUBJ-TOPIC-001)")
    
    # prerequisites 格式检查
    if 'prerequisites' in node:
        for prereq in node['prerequisites']:
            if 'id' not in prereq:
                errors.append(f"[{filepath}] prerequisites 缺少 id 字段")
            if 'required' not in prereq:
                errors.append(f"[{filepath}] prerequisites 缺少 required 字段")
    
    return errors

def validate_all():
    """校验所有数据文件"""
    base_path = Path(__file__).parent.parent
    subjects_path = base_path / 'subjects'
    
    all_errors = []
    all_ids = set()
    
    # 遍历所有知识点文件
    for yaml_file in subjects_path.rglob('*.yaml'):
        node = load_yaml(yaml_file)
        if '_error' in node:
            all_errors.append(f"[{yaml_file}] YAML 解析错误: {node['_error']}")
            continue
        
        # 检查 ID 唯一性
        if 'id' in node:
            if node['id'] in all_ids:
                all_errors.append(f"[{yaml_file}] ID 重复: {node['id']}")
            all_ids.add(node['id'])
        
        # 校验节点
        errors = validate_node(node, yaml_file.relative_to(base_path))
        all_errors.extend(errors)
    
    # 检查关系文件中的 ID 是否存在
    relations_path = base_path / 'relations'
    if relations_path.exists():
        for rel_file in relations_path.rglob('*.yaml'):
            rel_data = load_yaml(rel_file)
            if 'edges' in rel_data:
                for edge in rel_data['edges']:
                    if 'from' in edge and edge['from'] not in all_ids:
                        all_errors.append(f"[{rel_file}] 引用了不存在的 ID: {edge['from']}")
                    if 'to' in edge and edge['to'] not in all_ids:
                        all_errors.append(f"[{rel_file}] 引用了不存在的 ID: {edge['to']}")
    
    return all_errors

def main():
    print("🔍 AISTEC Knowledge Graph 数据校验")
    print("=" * 50)
    
    errors = validate_all()
    
    if not errors:
        print("✅ 所有数据校验通过！")
        return 0
    else:
        print(f"❌ 发现 {len(errors)} 个问题:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
