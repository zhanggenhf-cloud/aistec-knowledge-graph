# AISTEC 知识图谱 Schema 规范

## 版本
Schema Version: 1.0.0

## 知识点节点 Schema

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识符，格式：{学科代码}-{主题代码}-{序号} |
| `name` | string | 中文名称 |
| `subject` | string | 所属学科，枚举：物理/化学/生物/地球科学/天文学 |
| `grade` | string | 目标学段，如：小学三年级/初中八年级/高中一年级 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name_en` | string | 英文名称 |
| `domain` | string | 子领域，如：力学/热学/电磁学 |
| `description` | string | 概念描述 |
| `prerequisites` | array | 前置知识列表 |
| `postrequisites` | array | 后续知识列表 |
| `key_concepts` | array | 核心概念分解 |
| `misconceptions` | array | 常见误解 |
| `cognitive_level` | object | 认知发展层级 |
| `activity_suggestions` | array | 教学活动建议 |
| `verification` | object | 科学准确性验证 |
| `interdisciplinary` | array | 跨学科连接 |
| `exhibits` | array | 科技馆展品关联 |

### ID 编码规范

```
{学科代码}-{主题代码}-{序号}

学科代码：
  PHYS = 物理
  CHEM = 化学
  BIO = 生物
  EARTH = 地球科学
  ASTR = 天文学
  MATH = 数学（支撑学科）
  SCI = 小学科学

主题代码（物理示例）：
  FORCE = 力
  MOTION = 运动
  ENERGY = 能量
  WAVE = 波
  ELEC = 电
  MAG = 磁
  THERMO = 热力学

序号：3位数字，同一主题下自增
```

## 关系 Schema

### 边类型

| 类型 | 说明 |
|------|------|
| `prerequisite` | 前置知识（必须先学） |
| `postrequisite` | 后续知识（本概念是基础） |
| `related` | 相关概念（非线性关系） |
| `analogous` | 类比关系（如：水流-电流） |
| `application` | 应用关系（理论→实践） |

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

## 数据校验规则

1. **ID 唯一性**：所有知识点 ID 全局唯一
2. **关系完整性**：prerequisites 和 postrequisites 必须双向对应
3. **无环图**：知识依赖关系必须是有向无环图（DAG）
4. **年级递增**：前置知识的年级不应高于后续知识
5. **必填字段**：id, name, subject, grade 不能为空
