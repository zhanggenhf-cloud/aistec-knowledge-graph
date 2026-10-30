# AISTEC 知识图谱 Schema 规范

## 版本
Schema Version: 1.1.0（向后兼容扩展，与 1.0 数据完全兼容）

1.1 版借鉴 GitHub 项目 [xiaoyang111222/cn-math-taxonomy](https://github.com/xiaoyang111222/cn-math-taxonomy)（中小学知识图谱 + 自适应前置诊断）的成熟设计，新增守门诊断题、可观测掌握判据、课标对齐置信度等字段。配套集成指南见 aistec-skills 仓库 `skills/science-edu-activity/references/knowledge-graph.md`。

## 知识点节点 Schema

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识符，格式：{学科代码}-{主题代码}-{序号} |
| `name` | string | 中文名称 |
| `subject` | string | 所属学科，枚举：物理/化学/生物/地球科学/天文学/地理/历史/数学/信息科技/劳动/艺术/综合实践/小学科学 |
| `grade` | string | 目标学段，如：小学三年级/初中八年级/高中一年级 |

### 核心字段（Schema 1.0）

| 字段 | 类型 | 说明 |
|------|------|------|
| `name_en` | string | 英文名称 |
| `domain` | string | 子领域，如：力学/热学/电磁学 |
| `description` | string | 概念描述 |
| `prerequisites` | array | 前置知识列表，`[{id, name, required}]` |
| `postrequisites` | array | 后续知识列表 |
| `key_concepts` | array | 核心概念分解 |
| `misconceptions` | array | 常见误解（1.1 升级，见下） |
| `cognitive_level` | object | 认知发展层级 |
| `activity_suggestions` | array | 教学活动建议 |
| `verification` | object | 科学准确性验证 |
| `interdisciplinary` | array | 跨学科连接 |
| `exhibits` | array | 科技馆展品关联 |

### 新增字段（Schema 1.1，全部可选）

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | enum | `conceptual`（概念性）/ `procedural`（程序性）。决定诊断题提问方式：概念性用解释/辨析题，程序性用操作/计算题 |
| `semester` | string | 学期：`上` / `下` |
| `chapter` | string | 教材锚定，格式 `{册} 第{单元} {单元名}`；标注版本时 `人教版·八年级下册 第8章` |
| `mastery_criteria` | array<string> | 2–4 条**可观测**掌握判据，"能做 X"句式，禁用"理解/掌握"等不可测词；同时是诊断题的评分依据 |
| `diagnostic_question` | object | 守门诊断题：`{question, answer, acceptable_answers?, criteria_map?}`。每节点 1 道，答案确定可判定，优先暴露已知误解 |
| `standards` | array<object> | 课标对齐：`[{id, confidence}]`，confidence ∈ `exact` / `partial` / `unverified` |
| `root_reason` | string | 仅根节点（无先修边）必填：说明为什么它是图的起点 |
| `math_links` | array<object> | 本概念用到的数学工具：`[{id, name, usage}]`。是"用法引用"而非先修边，不进入诊断回溯 |
| `elective` | bool | 选学内容标记。`true` 不进入诊断回溯链 |

### misconception 五元组（Schema 1.1 升级）

```yaml
misconceptions:
  - statement: "误解表述（学习者原话风格）"
    correction: "正确理解"
    source: "文献来源（可选）"
    prevalence: high            # very_high / high / medium / low，决定干预优先级
    distractor: "由本误解派生的干扰项"   # 题库干扰项必须可溯源到此字段
    targeted_activity: "针对性微活动设计"  # 供 POE 预测环节等活动直接取用
```

`statement` / `correction` 为 1.0 已有；`source` 1.0 可选；`prevalence` / `distractor` / `targeted_activity` 为 1.1 新增，可选。

### ID 编码规范

```
{学科代码}-{主题代码}-{序号}

学科代码：
  PHYS = 物理        CHEM = 化学       BIO = 生物
  EARTH = 地球科学    ASTR = 天文学      MATH = 数学（支撑学科）
  SCI = 小学科学      GEO = 地理        HIS = 历史
  IT = 信息科技       LAB = 劳动        ART = 艺术
  COMP = 综合实践

主题代码（物理示例）：
  FORCE = 力    MOTION = 运动   ENERGY = 能量   WAVE = 波
  ELEC = 电     MAG = 磁        THERMO = 热力学

序号：3位数字，同一主题下自增
```

## 关系 Schema

### 边类型（Schema 1.1 细化）

| 类型 | 说明 | 进入诊断回溯 |
|------|------|--------------|
| `direct_prerequisite` | 直接先修（必须先学） | 是 |
| `foundational_experience` | 基础经验（低年级铺垫/感性经验，回溯终止层） | 是（终止层） |
| `related` | 相关概念（非线性关系） | 否 |
| `analogous` | 类比关系（如：水流-电流） | 否 |
| `application` | 应用关系（理论→实践） | 否 |

1.0 数据中的 `prerequisite` 边默认视为 `direct_prerequisite`。

### 强度等级

| 等级 | 说明 |
|------|------|
| `strong` | 必须掌握，缺失会导致严重理解困难 |
| `moderate` | 推荐掌握，缺失会增加学习难度 |
| `weak` | 拓展关联，了解即可 |

## 认知发展层级 Schema

| 字段 | 类型 | 说明 |
|------|------|------|
| `min_age` | integer | 最小认知年龄（岁） |
| `piaget_stage` | string | 皮亚杰阶段：感知运动/前运算/具体运算/形式运算 |
| `prerequisite_reasoning` | string | 所需思维类型 |

## 分科成图与跨科引用规则（Schema 1.1 新增）

借鉴 cn-math-taxonomy"分科成图、受控连边"设计：

1. 每门学科**独立成图**，先修边只在本学科图内延伸，不做跨学科先修链；
2. 跨科依赖一律用引用字段：用到的数学写 `math_links`，跨学科关联写 `interdisciplinary`，展品写 `exhibits`——这些引用供活动设计参考，**不构成诊断阻断**；
3. 诊断回溯允许沿 `direct_prerequisite` 跨学段下探到小学段，但终止于 `foundational_experience` 层。

## 课标对齐 ID 格式（Schema 1.1 新增）

```
{标准代码}:{学段}.{领域}.{序号}
```

| 标准代码 | 标准 |
|----------|------|
| `cs-2022-sci` | 《义务教育科学课程标准（2022年版）》 |
| `cs-2022-phy` | 《义务教育物理课程标准（2022年版）》 |
| `cs-2022-chem` | 《义务教育化学课程标准（2022年版）》 |
| `cs-2022-bio` | 《义务教育生物学课程标准（2022年版）》 |
| `cs-2022-geo` | 《义务教育地理课程标准（2022年版）》 |
| `cs-2022-his` | 《义务教育历史课程标准（2022年版）》 |
| `cs-2017-phy` | 《普通高中物理课程标准（2017年版2020年修订）》 |

置信度定义：`exact` = 条目内容与本节点实质等价；`partial` = 条目覆盖本节点的一部分；`unverified` = 已标注待人工复核。

## 数据校验规则

| # | 规则 | 级别 |
|---|------|------|
| R1 | ID 全局唯一 | error |
| R2 | prerequisites / postrequisites 双向对应 | error |
| R3 | 知识依赖关系为 DAG（无环） | error |
| R4 | 前置知识的年级不高于后续知识 | error |
| R5 | id / name / subject / grade 非空 | error |
| R6 | 根节点（无先修边）必须填写 `root_reason` | error |
| R7 | 守门诊断题覆盖率：核心节点 100%，全部节点 ≥ 95% | warning |
| R8 | 课标对齐覆盖率 ≥ 90%，`unverified` 占比 ≤ 10% | warning |
| R9 | 题库干扰项可溯源到 misconception.distractor（题库落地后启用） | warning |
| R10 | 无孤立节点（既无先修亦无后续的节点必须有 `root_reason`） | warning |
| R11 | 每学科图主连通分量覆盖 ≥ 95% 节点 | warning |

所有 `error` 必须修复后才能发布版本；`warning` 记入 CHANGELOG 限期补齐。校验工具输出 `verification_report.json`（见 `tools/validate.py --report`）。

## 范围决策（不建点的情形）

| 情形 | 处理方式 |
|------|----------|
| 课标中的选学内容 | 建点但标 `elective: true`，不进入诊断回溯链 |
| 超出课标的拓展/竞赛内容 | 不建点 |
| 涉及科学争议、伦理决策、社会政策（SSI）的话题 | 不建点，转人工设计 |
| 跨学科应用实例 | 不建点，写入 `interdisciplinary` |
