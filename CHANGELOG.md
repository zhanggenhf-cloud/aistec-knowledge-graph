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
- 11 个根节点补齐 `root_reason`（断环修复后 SCI-EARTH-001 成为第 12 个根节点，已同步补齐）
- 有 misconceptions 的节点均含暴露误解的判据，诊断题优先激活误解设问角度
- 迁移后覆盖率：diagnostic_question 100%、mastery_criteria 100%、misconception 100%（standard 字段本轮不迁移，见下）

### 本轮刻意不做（后续迭代）

- `chapter` / `semester` / `standards` / `math_links` 需要教材与课标原文外部知识，留待人工或专项迭代补充（当前 standards 覆盖率 0%）
- misconception 的 `prevalence` / `distractor` / `targeted_activity` 三新字段待逐条人工标注

### 数据修复（校验全绿）

- **R2 双向引用补全 ×187**（93 个文件，文本级插入保留原格式）：prerequisites 缺反向 postrequisite 123 处 + postrequisites 缺反向 prerequisite 64 处，全部补齐
- **R3 依赖环 ×2 修复**：BIO-DIV-001↔BIO-DIV-002（断为 多样性→分类 单向）、SCI-EARTH-001↔SCI-MOON-001（断为 太阳系运动→月相 单向），21 个下游阻塞节点自动解锁；SCI-EARTH-001 成为根节点并补 root_reason（根节点 11→12）
- **R5 required 字段补全 ×44**（存量条目缺失，统一补 `required: false` 保守非阻断，建议人工复核哪些应为 true）
- **校验器 R3 升级**：拓扑排序误报改为强连通分量（SCC）精确定位成环节点并打印节点名
- 修复后校验：**0 错误**；剩余 2 条警告为存量语义问题（IT-IOT→IT-AI 年级倒挂疑似课程设计意图、历史学科图碎片化），需人工判断
- 副作用：R2 补全同时打通了劳动学科图的跨组件连接（R11 劳动警告消除）

### 已知问题（由新校验规则首次暴露，存量数据，另行修复）

- ~~R2 × 187~~ ✅ 已修复
- ~~R3 依赖环~~ ✅ 已修复（SCC 确认无环）
- **R4（warning）**：IT-IOT-001（八年级）作为 IT-AI-001（七年级）先修，疑似跨学段课程设计，待确认
- **R11（warning）**：历史学科图主连通分量仅覆盖 56% 节点，存在碎片子图
