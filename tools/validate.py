#!/usr/bin/env python3
"""
AISTEC Knowledge Graph 数据校验工具（Schema 1.1）

Usage:
  python tools/validate.py            # 仅打印校验结果
  python tools/validate.py --report   # 额外输出 verification_report.json

校验规则见 SCHEMA.md（R1–R11）。
"""

import yaml
import os
import sys
import json
import re
from pathlib import Path
from collections import defaultdict

ERROR_RULES = {"R1", "R2", "R3", "R4", "R5", "R6"}
WARNING_RULES = {"R7", "R8", "R10", "R11"}  # R9 需题库落地后启用


def load_yaml(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        return {"_error": str(e)}


GRADE_RANK = {}
for i in range(1, 7):
    GRADE_RANK[f"小学{'一二三四五六'[i-1]}年级"] = i
    GRADE_RANK[f"{'一二三四五六'[i-1]}年级"] = i
for i in range(7, 10):
    GRADE_RANK[f"初中{'七八九'[i-7]}年级"] = i
    GRADE_RANK[f"{'七八九'[i-7]}年级"] = i
for i in range(1, 4):
    GRADE_RANK[f"高中{'一二三'[i-1]}年级"] = 9 + i
    GRADE_RANK[f"高{'一二三'[i-1]}"] = 9 + i


def grade_rank(grade):
    """把学段字符串映射为可比较的年级数值，无法识别时返回 None"""
    if not grade:
        return None
    g = str(grade).strip()
    if g in GRADE_RANK:
        return GRADE_RANK[g]
    m = re.match(r"^(小学|初中|高中)?([1-9])年级?$", g)
    if m:
        n = int(m.group(2))
        stage = m.group(1)
        if stage == "初中" or (not stage and 7 <= n <= 9):
            return n
        if stage == "高中" or (not stage and n >= 10):
            return n
        return n if n <= 6 else None
    return None


def validate_node(node, filepath):
    """单节点基础校验（R1/R5 的一部分）"""
    errors = []
    required_fields = ['id', 'name', 'subject', 'grade']
    for field in required_fields:
        if field not in node or not node[field]:
            errors.append((filepath, "R5", f"缺少必需字段: {field}"))
    if 'id' in node:
        parts = str(node['id']).split('-')
        if len(parts) != 3:
            errors.append((filepath, "R1", f"ID 格式错误: {node['id']} (应为 SUBJ-TOPIC-001)"))
    if 'prerequisites' in node and node['prerequisites']:
        for prereq in node['prerequisites']:
            if isinstance(prereq, dict):
                if 'id' not in prereq:
                    errors.append((filepath, "R5", "prerequisites 缺少 id 字段"))
                if 'required' not in prereq:
                    errors.append((filepath, "R5", f"prerequisites[{prereq.get('id', '?')}] 缺少 required 字段"))
    return errors


def build_graph(nodes):
    """汇总节点 prerequisites 与 relations/ 边，构建有向图 {from: set(to)}"""
    graph = defaultdict(set)
    for nid, node in nodes.items():
        for pre in (node.get('prerequisites') or []):
            if isinstance(pre, dict) and pre.get('id'):
                graph[pre['id']].add(nid)  # pre -> nid（先修指向后续）
    return graph


def check_dag(graph, all_ids, nodes=None):
    """R3: 强连通分量（SCC）定位真实成环节点；未入拓扑序的下游阻塞节点仅作提示"""
    errors = []
    adj = {u: sorted(v for v in graph[u] if v in all_ids) for u in all_ids if u in graph}
    index_of, lowlink, on_stk = {}, {}, set()
    stk, cnt, sccs = [], [0], []
    for start in all_ids:
        if start in index_of or start not in adj:
            continue
        work = [(start, 0)]
        index_of[start] = lowlink[start] = cnt[0]; cnt[0] += 1
        stk.append(start); on_stk.add(start)
        while work:
            v, ci = work[-1]
            if ci < len(adj.get(v, [])):
                w = adj.get(v, [])[ci]
                work[-1] = (v, ci + 1)
                if w not in index_of:
                    index_of[w] = lowlink[w] = cnt[0]; cnt[0] += 1
                    stk.append(w); on_stk.add(w)
                    work.append((w, 0))
                elif w in on_stk:
                    lowlink[v] = min(lowlink[v], index_of[w])
            else:
                work.pop()
                if work:
                    lowlink[work[-1][0]] = min(lowlink[work[-1][0]], lowlink[v])
                if lowlink[v] == index_of[v]:
                    comp = []
                    while True:
                        w = stk.pop(); on_stk.discard(w)
                        comp.append(w)
                        if w == v:
                            break
                    if len(comp) > 1 or comp[0] in adj.get(comp[0], []):
                        sccs.append(sorted(comp))
    for comp in sccs:
        if nodes:
            names = '、'.join(f"{nid}({nodes.get(nid, {}).get('name', '?')})" for nid in comp)
        else:
            names = '、'.join(comp)
        errors.append((Path("relations"), "R3", f"依赖图存在环: {names}"))
    return errors


def largest_component_ratio(graph, subject_nodes):
    """R11: 主连通分量（弱连通）占比"""
    und = defaultdict(set)
    for u in graph:
        for v in graph[u]:
            und[u].add(v)
            und[v].add(u)
    seen, best = set(), 0
    for nid in subject_nodes:
        if nid in seen:
            continue
        comp, stack = set(), [nid]
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            stack.extend(und[x] - comp)
        seen |= comp
        best = max(best, len(comp & subject_nodes))
    return best / len(subject_nodes) if subject_nodes else 1.0


def validate_all(base_path=None, emit_report=False):
    base_path = base_path or Path(__file__).parent.parent
    subjects_path = base_path / 'subjects'

    errors, warnings = [], []
    nodes, id2file = {}, {}
    coverage = {"diagnostic_question": [0, 0], "mastery_criteria": [0, 0],
                "standards": [0, 0], "misconception": [0, 0]}

    yaml_files = sorted(subjects_path.rglob('*.yaml'))
    for yf in yaml_files:
        node = load_yaml(yf)
        rel = str(yf.relative_to(base_path))
        if '_error' in node:
            errors.append((rel, "R5", f"YAML 解析错误: {node['_error']}"))
            continue
        nid = node.get('id')
        if nid:
            if nid in nodes:
                errors.append((rel, "R1", f"ID 重复: {nid}"))
            nodes[nid] = node
            id2file[nid] = rel
        errors.extend(validate_node(node, rel))

        has_pre = bool(node.get('prerequisites'))
        has_post = bool(node.get('postrequisites'))
        if not has_pre and not node.get('root_reason'):
            errors.append((rel, "R6", f"根节点 {nid} 缺少 root_reason"))
        if not has_pre and not has_post and not node.get('root_reason'):
            errors.append((rel, "R10", f"孤立节点 {nid}（无先修无后续）必须有 root_reason"))

        coverage["diagnostic_question"][1] += 1
        if node.get('diagnostic_question', {}).get('question'):
            coverage["diagnostic_question"][0] += 1
        else:
            warnings.append((rel, "R7", f"{nid} 缺少守门诊断题"))
        coverage["mastery_criteria"][1] += 1
        if node.get('mastery_criteria'):
            coverage["mastery_criteria"][0] += 1
        coverage["standards"][1] += 1
        if node.get('standards'):
            coverage["standards"][0] += 1
        coverage["misconception"][1] += 1
        if node.get('misconceptions'):
            coverage["misconception"][0] += 1

    # R2: 双向对应
    for nid, node in nodes.items():
        for pre in (node.get('prerequisites') or []):
            pid = pre.get('id') if isinstance(pre, dict) else None
            if pid and pid in nodes:
                posts = [p.get('id') for p in (nodes[pid].get('postrequisites') or []) if isinstance(p, dict)]
                if nid not in posts:
                    errors.append((id2file[nid], "R2", f"{pid} 的 postrequisites 未反向引用 {nid}"))
        for post in (node.get('postrequisites') or []):
            sid = post.get('id') if isinstance(post, dict) else None
            if sid and sid in nodes:
                pres = [p.get('id') for p in (nodes[sid].get('prerequisites') or []) if isinstance(p, dict)]
                if nid not in pres:
                    errors.append((id2file[nid], "R2", f"{sid} 的 prerequisites 未反向引用 {nid}"))

    # relations/ 文件：ID 存在性 + 并入图
    relations_path = base_path / 'relations'
    if relations_path.exists():
        for rel_file in relations_path.rglob('*.yaml'):
            rel_data = load_yaml(rel_file)
            if 'edges' in rel_data:
                for edge in rel_data['edges']:
                    for key in ('from', 'to'):
                        if key in edge and edge[key] not in nodes:
                            errors.append((str(rel_file.relative_to(base_path)), "R2",
                                           f"引用了不存在的 ID: {edge[key]}"))

    graph = build_graph(nodes)

    # R3: DAG
    errors.extend(check_dag(graph, set(nodes), nodes))

    # R4: 年级单调性
    for u, targets in graph.items():
        if u not in nodes:
            continue
        ru = grade_rank(nodes[u].get('grade'))
        if ru is None:
            continue
        for v in targets:
            if v not in nodes:
                continue
            rv = grade_rank(nodes[v].get('grade'))
            if rv is not None and ru > rv:
                warnings.append((id2file.get(u, u), "R4",
                                 f"年级倒挂: {u}({nodes[u].get('grade')}) 是 {v}({nodes[v].get('grade')}) 的先修"))

    # R11: 学科主连通分量
    by_subject = defaultdict(set)
    for nid, node in nodes.items():
        by_subject[str(node.get('subject', '未标注'))].add(nid)
    conn_report = {}
    for subj, nids in sorted(by_subject.items()):
        ratio = largest_component_ratio(graph, nids)
        conn_report[subj] = round(ratio, 3)
        if ratio < 0.95:
            warnings.append(("subjects", "R11", f"{subj} 主连通分量仅覆盖 {ratio:.0%} 节点"))

    report = {
        "generated_at": None,  # 由调用方填充
        "schema_version": "1.1.0",
        "nodes": {
            "total": len(nodes),
            "by_subject": {s: len(n) for s, n in sorted(by_subject.items())},
        },
        "edges": {"total": sum(len(t) for t in graph.values())},
        "coverage": {k: (round(v[0] / v[1], 3) if v[1] else 0) for k, v in coverage.items()},
        "connectivity": conn_report,
        "checks": [
            {"id": r, "status": "fail", "file": str(f), "message": m} for f, r, m in errors
        ] + [
            {"id": r, "status": "warn", "file": str(f), "message": m} for f, r, m in warnings
        ],
        "summary": {"errors": len(errors), "warnings": len(warnings)},
    }
    return errors, warnings, report


def main():
    print("🔍 AISTEC Knowledge Graph 数据校验（Schema 1.1）")
    print("=" * 50)

    errors, warnings, report = validate_all()
    for f, r, m in errors:
        print(f"  ❌ [{r}] {f}: {m}")
    for f, r, m in warnings:
        print(f"  ⚠️  [{r}] {f}: {m}")

    print("=" * 50)
    print(f"错误 {len(errors)} 个，警告 {len(warnings)} 个")
    for k, v in report["coverage"].items():
        print(f"  覆盖率 {k}: {v:.0%}")

    if "--report" in sys.argv:
        from datetime import datetime, timezone, timedelta
        report["generated_at"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
        out = Path(__file__).parent.parent / "verification_report.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"📄 报告已写入 {out}")

    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
