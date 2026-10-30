# CHANGELOG

## [1.1.0] - 2026-10-30

Schema 1.1 向后兼容扩展。数据模型借鉴 [xiaoyang111222/cn-math-taxonomy](https://github.com/xiaoyang111222/cn-math-taxonomy)（中小学知识图谱 + 自适应前置诊断）的成熟设计。配套集成指南见 aistec-skills 仓库 `skills/science-edu-activity/references/knowledge-graph.md`。

### 新增（Schema 1.1，全部可选）

- 节点字段：`type`（conceptual/procedural）、`semester`、`chapter`、`mastery_criteria`（可观测掌握判据）、`diagnostic_question`（守门诊断题）、`standards`（课标对齐含 exact/partial/unverified 置信度）、`root_reason`（根节点必填）、`math_links`（跨科数学用法引用，非先修边）、`elective`（选学标记，不进诊断回溯链）
- misconception 五元组扩展：`prevalence`、`distractor`（题库干扰项必须可溯源）、`targeted_activity`
- 边类型细化：`direct_prerequisite` vs `foundational_experience`（回溯终止层）；1.0 的 `prerequisite` 默认视为 `direct_prerequisite`
- 分科成图规则：先修边只在学科图内延伸，跨科依赖一律走 `math_links` / `interdisciplinary` / `exhibits` 引用字段
- 课标对齐 ID 格式：`cs-2022-sci:{学段}.{领域}.{序号}` 等（见 SCHEMA.md）
- 校验规则 R1–R11 与 `verification_report.json` 输出（`python tools/validate.py --report`）

### 数据迁移（178 个节点全部完成）

- 178/178 节点追加 `type` + `mastery_criteria`（2–3 条）+ `diagnostic_question`
  - conceptual 148 个 / procedural 30 个
- 11 个根节点补齐 `root_reason`
- 有 misconceptions 的节点均含暴露误解的判据，诊断题优先激活误解设问角度
- 迁移后覆盖率：diagnostic_question 100%、mastery_criteria 100%、misconception 100%（standard 字段本轮不迁移，见下）

### 本轮刻意不做（后续迭代）

- `chapter` / `semester` / `standards` / `math_links` 需要教材与课标原文外部知识，留待人工或专项迭代补充（当前 standards 覆盖率 0%）
- misconception 的 `prevalence` / `distractor` / `targeted_activity` 三新字段待逐条人工标注

### 已知问题（由新校验规则首次暴露，存量数据，另行修复）

- **R2 × 187**：prerequisites/postrequisites 双向引用不一致（大量节点缺失反向引用）
- **R3**：依赖图存在环，约 25 个节点涉及（如 PHYS-HEAT-004 ↔ PHYS-ELEC-007 互相引用），需人工梳理拓扑
- **R11**：劳动、历史两个学科图主连通分量仅覆盖 50%–56% 节点，存在碎片子图
