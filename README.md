# AISTEC 科学知识图谱

AISTEC 知识图谱（Knowledge Graph）是 science-edu-activity 技能的底层知识基础设施，将分散的教材知识点转化为结构化的概念网络，支持：

- **前置知识诊断**：自动识别学习者缺失的先备概念
- **学习路径规划**：基于依赖关系生成最优学习序列
- **跨年级衔接**：打通小学科学→初中物理→高中力学的概念断层
- **活动设计支撑**：为 AISTEC 框架匹配提供知识点级别的精度

## 数据结构

### 1. 知识点节点（Node）

每个知识点存储在 `subjects/` 目录下，文件名为 `{subject}/{concept-id}.yaml`：

```yaml
id: PHYS-FORCE-001           # 唯一标识：学科-主题-序号
name: 力的概念                # 中文名称
name_en: Concept of Force     # 英文名称
subject: 物理                  # 所属学科
domain: 力学                   # 子领域
grade: 初中八年级              # 目标学段

description: |
  力是物体对物体的作用。理解力的三要素（大小、方向、作用点）
  以及力的相互性（作用力与反作用力）。

# 前置知识（必须掌握才能学习本概念）
prerequisites:
  - id: MATH-VEC-001          # 向量的基本概念
    required: true             # true=必须, false=推荐
  - id: SCI-MOT-001          # 小学科学：运动与力
    required: true

# 后续知识（本概念是哪些知识的基础）
postrequisites:
  - id: PHYS-FORCE-002        # 重力
  - id: PHYS-FORCE-003        # 弹力
  - id: PHYS-NEWTON-001       # 牛顿第一定律

# 核心概念分解
key_concepts:
  - term: 力的定义
    definition: 力是物体对物体的作用
    importance: 核心
  - term: 力的三要素
    definition: 大小、方向、作用点
    importance: 核心
  - term: 力的相互性
    definition: 物体间力的作用是相互的
    importance: 核心

# 常见误解（教学难点）
misconceptions:
  - statement: "力是维持物体运动的原因"
    correction: "力是改变物体运动状态的原因，不是维持"
    source: Clement, 1982
  - statement: "只有接触的物体之间才有力的作用"
    correction: "非接触力（重力、磁力）不需要接触"

# 认知发展层级（基于皮亚杰/维果茨基）
cognitive_level:
  min_age: 12                  # 最小认知年龄
  piaget_stage: 形式运算阶段   # 对应皮亚杰阶段
  prerequisite_reasoning: 抽象思维  # 需要的思维类型

# 教学活动建议（与 AISTEC 框架对接）
activity_suggestions:
  - framework: POE             # 推荐教学法框架
    brief: 预测不同表面推箱子的感受，体验力的相互性
  - framework: 5E
    brief: Engage用磁铁隔空吸引，Explore测量不同拉力

# 科学准确性验证
verification:
  status: verified             # verified / draft / disputed
  sources:
    - "Halliday, Resnick & Walker. Fundamentals of Physics. 10th ed."
  last_verified: 2024-06-01

# 跨学科连接
interdisciplinary:
  - subject: 数学
    concept: 向量运算
    relation: 工具支撑
  - subject: 生物
    concept: 肌肉收缩
    relation: 应用实例

# 博物馆/科技馆展品关联
exhibits:
  - venue: 中国科技馆
    name: 万有引力展品
    relation: 演示重力的非接触性
```

### 2. 关系图谱（Relation）

关系存储在 `relations/` 目录下，支持复杂依赖查询：

```yaml
# relations/force-chain.yaml
relation_chain: 力的概念→重力→弹力→摩擦力→牛顿定律
edges:
  - from: PHYS-FORCE-001
    to: PHYS-FORCE-002
    type: prerequisite          # 前置关系
    strength: strong            # strong / moderate / weak
  - from: PHYS-FORCE-001
    to: PHYS-FORCE-003
    type: prerequisite
    strength: strong
```

### 3. 年级映射（Grade Map）

`grade-maps/` 定义每个年级的知识点覆盖：

```yaml
# grade-maps/junior-8-physics.yaml
grade: 初中八年级
subject: 物理
semester: 上学期
topics:
  - chapter: 机械运动
    concepts:
      - PHYS-MOTION-001        # 机械运动
      - PHYS-MOTION-002        # 速度
  - chapter: 声现象
    concepts:
      - PHYS-SOUND-001         # 声音的产生
      - PHYS-SOUND-002         # 声音的传播
```

## 目录结构

```
aistec-knowledge-graph/
├── README.md                 # 本文档
├── SCHEMA.md                 # 完整数据 schema 规范
├── subjects/                 # 知识点节点
│   ├── physics/              # 物理
│   │   ├── mechanics/        # 力学
│   │   ├── thermodynamics/   # 热学
│   │   └── electromagnetism/ # 电磁学
│   ├── chemistry/            # 化学
│   ├── biology/              # 生物
│   ├── earth-science/        # 地球科学
│   └── astronomy/            # 天文学
├── relations/                # 关系定义
│   ├── physics-chains.yaml
│   └── cross-subject.yaml
├── grade-maps/               # 年级课程映射
│   ├── primary-3-science.yaml
│   ├── primary-6-science.yaml
│   ├── junior-8-physics.yaml
│   └── senior-1-physics.yaml
├── examples/                 # 使用示例
│   ├── query-examples.md
│   └── aistec-integration.md
└── tools/                    # 工具脚本
    ├── validate.py           # 数据校验
    └── query.py              # 依赖查询
```

## 与 AISTEC 技能集成

### 使用场景 1：前置知识诊断

当用户输入"设计一个关于牛顿第一定律的活动"时，AISTEC 自动查询：

```yaml
# AISTEC 内部查询
query:
  target: PHYS-NEWTON-001
  need_prerequisites: true
  max_depth: 2                  # 查2层前置知识
```

返回结果：
```
学习者必须掌握的前置知识：
1. 力的概念 (PHYS-FORCE-001) - 必须
2. 运动与速度 (PHYS-MOTION-002) - 必须
3. 惯性（日常概念）(SCI-INERTIA-001) - 推荐

如果学习者缺失 PHYS-FORCE-001，建议先补充"力的概念"活动
```

### 使用场景 2：学习路径生成

```yaml
query:
  start: SCI-MOT-001            # 小学：运动与力
  end: PHYS-NEWTON-001          # 高中：牛顿定律
  path_type: shortest           # shortest / comprehensive
```

返回结果：
```
推荐学习路径（最短）：
SCI-MOT-001 → PHYS-FORCE-001 → PHYS-FORCE-002 
→ PHYS-FORCE-005 → PHYS-NEWTON-001

共 5 个概念节点，预计学习时长：6-8 课时
```

### 使用场景 3：跨年级衔接

当小学六年级学生进入初中物理时，系统识别：
```
小学已掌握：SCI-MOT-001 (运动与力)
初中新需求：PHYS-FORCE-001 (力的概念)
衔接建议：从"推箱子"日常经验过渡到"力的三要素"科学概念
```

## 贡献指南

1. 新增知识点：复制 `template.yaml` 填写，提交 PR
2. 修改关系：在 `relations/` 中更新边定义
3. 验证数据：运行 `python tools/validate.py`

## 数据来源

- 2022 版义务教育科学/物理课程标准
- 人教版、苏教版、北师大版教材目录
- NGSS（Next Generation Science Standards）跨学科概念映射
- 科学教育研究文献（前概念、认知发展）

## License

MIT — 与 AISTEC 技能集保持一致
