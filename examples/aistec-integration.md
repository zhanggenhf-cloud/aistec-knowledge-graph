# AISTEC 知识图谱集成指南

本文档说明如何在 AISTEC 框架中使用知识图谱。

## 集成点

### 1. 活动设计时的前置知识诊断

当用户输入活动主题时，AISTEC 自动查询知识图谱：

```python
# AISTEC 内部逻辑示例
def design_activity(topic):
    # 1. 识别知识点
    concept_id = kg.identify_concept(topic)  # 如 "牛顿第一定律" → PHYS-NEWTON-001
    
    # 2. 查询前置知识
    prerequisites = kg.get_prerequisites(concept_id, depth=2)
    
    # 3. 生成前置知识提示（内部使用）
    if prerequisites:
        internal_note = f"""
        本活动涉及 {concept_id}，学习者需要掌握以下前置知识：
        {format_prerequisites(prerequisites)}
        
        活动设计中应考虑：
        - 若学习者缺失前置知识，建议先进行快速回顾
        - 在活动中设置检查点，验证前置知识掌握情况
        """
    
    # 4. 继续正常的活动设计流程...
```

### 2. 生成活动方案时的知识解构

知识图谱的 `key_concepts` 和 `misconceptions` 直接支撑 Phase 2 的知识解构：

```yaml
# AISTEC Phase 2: Knowledge Deconstruction
# 自动从知识图谱提取：

knowledge_nodes:
  - concept: "惯性"  # ← 来自 key_concepts
    explanation: "物体保持原有运动状态的性质"
    misconceptions:  # ← 来自 misconceptions
      - "速度大的物体惯性大" → "惯性只与质量有关"
    
  - concept: "牛顿第一定律"
    real_world_example: "汽车急刹车时乘客前倾"
    activity_type: "POE"  # ← 来自 activity_suggestions
```

### 3. 跨年级衔接建议

当检测到用户输入的活动主题与学习者年级不匹配时：

```python
# 用户："给小学三年级设计一个关于惯性的活动"
# 系统查询：
concept = kg.get_concept("惯性")  # PHYS-NEWTON-001

if concept['grade'] == '初中八年级' and target_grade == '小学三年级':
    # 查询是否有低龄适配版本
    alternatives = kg.find_alternatives("惯性", max_grade="小学六年级")
    # 返回：SCI-MOT-001 "运动与力（小学）" 更合适
    
    suggestion = """
    注意："惯性"是初中物理概念（形式运算阶段）。
    对于小学三年级学生，建议改用：
    - 主题：运动与力（小学科学）
    - 核心经验：推/拉改变物体运动状态
    - 避免：牛顿定律的形式化表述
    """
```

### 4. 科技馆展品关联

知识图谱的 `exhibits` 字段直接支撑场景适配层：

```yaml
# 用户："设计一个关于重力的科技馆活动"
exhibits = kg.get_exhibits("PHYS-FORCE-002")
# 返回：中国科技馆"月球漫步"、"万有引力展品"

# AISTEC 自动在方案中插入：
venue_adaptation:
  recommended_exhibits:
    - name: "月球漫步"
      activity: "在不同重力环境下做同样的跳跃动作，记录感受差异"
```

## 数据更新流程

```
教师/专家提交知识点 → PR Review → 合并到主分支 → AISTEC 自动拉取更新
```

## 文件结构对应

| AISTEC 技能 | 知识图谱文件 |
|------------|-------------|
| SKILL.md Phase 2 | SCHEMA.md + subjects/*.yaml |
| knowledge-deconstruction.md | key_concepts, misconceptions |
| error-correction.md | verification.status |
| output-schema.md | grade-maps/*.yaml |
