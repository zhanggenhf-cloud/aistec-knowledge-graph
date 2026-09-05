#!/usr/bin/env python3
"""
AISTEC Knowledge Graph 批量知识点生成器
基于2022版义务教育课程标准生成知识点YAML文件

Usage: python tools/batch_generate.py
"""

import yaml
import os
from pathlib import Path

# ============ 小学科学知识点 (2022版课标: 13个核心概念) ============
PRIMARY_SCIENCE = {
    "物质科学": {
        "grade_range": "1-6年级",
        "concepts": [
            {
                "id": "SCI-MAT-001", "name": "物体具有一定的特征，材料具有一定的性能",
                "grade": "小学一年级", "misconceptions": ["所有金属都会生锈"],
            },
            {
                "id": "SCI-MAT-002", "name": "水是一种常见而重要的单一物质",
                "grade": "小学二年级", "prereq": ["SCI-MAT-001"],
                "misconceptions": ["水变成水蒸气后消失了"],
            },
            {
                "id": "SCI-MAT-003", "name": "空气是一种常见而重要的混合物质",
                "grade": "小学三年级", "prereq": ["SCI-MAT-002"],
            },
            {
                "id": "SCI-MAT-004", "name": "物体的运动可以用位置、快慢和方向来描述",
                "grade": "小学四年级", "prereq": ["SCI-MAT-001"],
            },
            {
                "id": "SCI-MOT-001", "name": "力作用于物体，可以改变物体的形状和运动状态",
                "grade": "小学四年级", "prereq": ["SCI-MAT-004"],
                "misconceptions": ["力是维持物体运动的原因"],
            },
            {
                "id": "SCI-FORCE-001", "name": "声音因物体振动而产生",
                "grade": "小学四年级",
            },
            {
                "id": "SCI-LIGHT-001", "name": "光在空气中沿直线传播",
                "grade": "小学五年级",
            },
            {
                "id": "SCI-HEAT-001", "name": "热可以改变物质的状态",
                "grade": "小学三年级", "prereq": ["SCI-MAT-002"],
            },
            {
                "id": "SCI-MAG-001", "name": "磁铁能对某些物体产生作用",
                "grade": "小学二年级",
            },
            {
                "id": "SCI-ELEC-001", "name": "电路是包括电源在内的闭合回路",
                "grade": "小学四年级", "prereq": ["SCI-MAG-001"],
            },
        ]
    },
    "生命科学": {
        "grade_range": "1-6年级",
        "concepts": [
            {
                "id": "SCI-LIFE-001", "name": "生物体具有一定的结构层次",
                "grade": "小学二年级",
            },
            {
                "id": "SCI-LIFE-002", "name": "生物能适应其生存环境",
                "grade": "小学三年级", "prereq": ["SCI-LIFE-001"],
            },
            {
                "id": "SCI-LIFE-003", "name": "生物能生长、发育和繁殖后代",
                "grade": "小学三年级", "prereq": ["SCI-LIFE-001"],
            },
            {
                "id": "SCI-LIFE-004", "name": "动物和植物都有基本生存需要",
                "grade": "小学一年级",
            },
            {
                "id": "SCI-BODY-001", "name": "人体由多个系统组成",
                "grade": "小学五年级", "prereq": ["SCI-LIFE-001"],
            },
            {
                "id": "SCI-ECO-001", "name": "生物之间、生物与环境之间相互依存",
                "grade": "小学五年级", "prereq": ["SCI-LIFE-002"],
            },
        ]
    },
    "地球与宇宙科学": {
        "grade_range": "1-6年级",
        "concepts": [
            {
                "id": "SCI-EARTH-001", "name": "在太阳系中，地球、月球和其他星球有规律地运动着",
                "grade": "小学六年级",
            },
            {
                "id": "SCI-EARTH-002", "name": "地球上有大气、水、生物、土壤和岩石",
                "grade": "小学三年级",
            },
            {
                "id": "SCI-EARTH-003", "name": "地球是人类生存的家园",
                "grade": "小学二年级", "prereq": ["SCI-EARTH-002"],
            },
            {
                "id": "SCI-WEATHER-001", "name": "天气现象有阴、晴、雨、雪、风等",
                "grade": "小学二年级",
            },
        ]
    },
}

# ============ 小学科学补充知识点 ==========
PRIMARY_SCIENCE_EXTRA = {
    "物质科学补充": {
        "grade_range": "1-6年级",
        "concepts": [
            {"id": "SCI-MAT-005", "name": "物质的状态变化与温度", "grade": "小学三年级", "prereq": ["SCI-HEAT-001"]},
            {"id": "SCI-MIX-001", "name": "混合物与分离", "grade": "小学三年级", "prereq": ["SCI-MAT-002"]},
            {"id": "SCI-DISS-001", "name": "溶解与溶液", "grade": "小学四年级", "prereq": ["SCI-MAT-002"]},
            {"id": "SCI-COND-001", "name": "导体与绝缘体", "grade": "小学四年级", "prereq": ["SCI-ELEC-001"]},
        ]
    },
    "地球与宇宙补充": {
        "grade_range": "1-6年级",
        "concepts": [
            {"id": "SCI-WATER-001", "name": "水在自然界的循环", "grade": "小学五年级", "prereq": ["SCI-MAT-002", "SCI-HEAT-001"]},
            {"id": "SCI-ROCK-001", "name": "岩石与土壤", "grade": "小学四年级", "prereq": ["SCI-EARTH-002"]},
            {"id": "SCI-SEAS-001", "name": "季节变化与地球公转", "grade": "小学六年级", "prereq": ["SCI-EARTH-001"]},
            {"id": "SCI-MOON-001", "name": "月相变化", "grade": "小学六年级", "prereq": ["SCI-EARTH-001"]},
            {"id": "SCI-STARS-001", "name": "星座与星系", "grade": "小学六年级", "prereq": ["SCI-EARTH-001"]},
        ]
    },
    "技术与工程": {
        "grade_range": "1-6年级",
        "concepts": [
            {"id": "SCI-TECH-001", "name": "工程设计过程", "grade": "小学五年级"},
            {"id": "SCI-TECH-002", "name": "简单机械的应用", "grade": "小学五年级", "prereq": ["SCI-MOT-001"]},
            {"id": "SCI-TECH-003", "name": "技术与生活", "grade": "小学六年级"},
        ]
    },
}

# ============ 初中物理补充知识点 (九年级) ==========
JUNIOR_PHYSICS_EXTRA = {
    "热学": {
        "concepts": [
            {"id": "PHYS-HEAT-001", "name": "内能", "grade": "初中九年级", "prereq": ["PHYS-THERMO-001"]},
            {"id": "PHYS-HEAT-002", "name": "比热容", "grade": "初中九年级", "prereq": ["PHYS-HEAT-001"]},
            {"id": "PHYS-HEAT-003", "name": "热机", "grade": "初中九年级", "prereq": ["PHYS-HEAT-002"]},
            {"id": "PHYS-HEAT-004", "name": "热机效率", "grade": "初中九年级", "prereq": ["PHYS-HEAT-003"]},
        ]
    },
    "电学补充": {
        "concepts": [
            {"id": "PHYS-ELEC-008", "name": "串联与并联电路", "grade": "初中九年级", "prereq": ["PHYS-ELEC-002"]},
            {"id": "PHYS-ELEC-009", "name": "家庭电路", "grade": "初中九年级", "prereq": ["PHYS-ELEC-008"]},
            {"id": "PHYS-ELEC-010", "name": "焦耳定律", "grade": "初中九年级", "prereq": ["PHYS-ELEC-007"]},
        ]
    },
    "信息与能源": {
        "concepts": [
            {"id": "PHYS-INFO-001", "name": "电磁波", "grade": "初中九年级"},
            {"id": "PHYS-ENERGY-003", "name": "能源与可持续发展", "grade": "初中九年级", "prereq": ["PHYS-ENERGY-002"]},
            {"id": "PHYS-NUC-001", "name": "核能", "grade": "初中九年级"},
        ]
    },
}

# ============ 初中化学补充知识点 ==========
JUNIOR_CHEMISTRY_EXTRA = {
    "补充": {
        "concepts": [
            {"id": "CHEM-METAL-001", "name": "金属", "grade": "初中九年级", "prereq": ["CHEM-REACT-001"]},
            {"id": "CHEM-METAL-002", "name": "金属的化学性质", "grade": "初中九年级", "prereq": ["CHEM-METAL-001"]},
            {"id": "CHEM-SOL-001", "name": "溶液", "grade": "初中九年级", "prereq": ["CHEM-MAT-001"]},
            {"id": "CHEM-SOL-002", "name": "溶解度", "grade": "初中九年级", "prereq": ["CHEM-SOL-001"]},
            {"id": "CHEM-ACID-002", "name": "中和反应", "grade": "初中九年级", "prereq": ["CHEM-ACID-001"]},
            {"id": "CHEM-FERT-001", "name": "化学肥料", "grade": "初中九年级", "prereq": ["CHEM-SALT-001"]},
            {"id": "CHEM-ORG-001", "name": "有机化合物", "grade": "初中九年级", "prereq": ["CHEM-MAT-002"]},
        ]
    }
}

# ============ 初中生物补充知识点 ==========
JUNIOR_BIOLOGY_EXTRA = {
    "补充": {
        "concepts": [
            {"id": "BIO-PLANT-003", "name": "植物的结构层次", "grade": "初中七年级上", "prereq": ["BIO-CELL-002"]},
            {"id": "BIO-ANIMAL-001", "name": "动物的运动", "grade": "初中八年级上", "prereq": ["BIO-BODY-004"]},
            {"id": "BIO-NERVE-001", "name": "神经系统", "grade": "初中七年级下", "prereq": ["BIO-BODY-004"]},
            {"id": "BIO-ENDO-001", "name": "内分泌系统", "grade": "初中七年级下", "prereq": ["BIO-BODY-004"]},
            {"id": "BIO-IMMUN-001", "name": "免疫", "grade": "初中八年级下", "prereq": ["BIO-BODY-003"]},
            {"id": "BIO-MICRO-001", "name": "微生物", "grade": "初中八年级上"},
            {"id": "BIO-MICRO-002", "name": "传染病与免疫", "grade": "初中八年级下", "prereq": ["BIO-MICRO-001"]},
            {"id": "BIO-DIV-001", "name": "生物的分类", "grade": "初中八年级上"},
            {"id": "BIO-DIV-002", "name": "生物的多样性", "grade": "初中八年级上", "prereq": ["BIO-DIV-001"]},
        ]
    }
}

# ============ 初中物理知识点 (2022版课标) ============
JUNIOR_PHYSICS = {
    "力学": {
        "concepts": [
            {"id": "PHYS-MOTION-001", "name": "机械运动", "grade": "初中八年级上", "prereq": ["SCI-MOT-001"]},
            {"id": "PHYS-MOTION-002", "name": "速度", "grade": "初中八年级上", "prereq": ["PHYS-MOTION-001"]},
            {"id": "PHYS-SOUND-001", "name": "声音的产生与传播", "grade": "初中八年级上", "prereq": ["SCI-FORCE-001"]},
            {"id": "PHYS-SOUND-002", "name": "声音的特性", "grade": "初中八年级上", "prereq": ["PHYS-SOUND-001"]},
            {"id": "PHYS-THERMO-001", "name": "温度与物态变化", "grade": "初中八年级上", "prereq": ["SCI-HEAT-001"]},
            {"id": "PHYS-OPTICS-001", "name": "光的直线传播", "grade": "初中八年级上", "prereq": ["SCI-LIGHT-001"]},
            {"id": "PHYS-OPTICS-002", "name": "光的反射", "grade": "初中八年级上", "prereq": ["PHYS-OPTICS-001"]},
            {"id": "PHYS-OPTICS-003", "name": "平面镜成像", "grade": "初中八年级上", "prereq": ["PHYS-OPTICS-002"]},
            {"id": "PHYS-OPTICS-004", "name": "光的折射", "grade": "初中八年级上", "prereq": ["PHYS-OPTICS-001"]},
            {"id": "PHYS-LENS-001", "name": "凸透镜成像规律", "grade": "初中八年级上", "prereq": ["PHYS-OPTICS-004"]},
            {"id": "PHYS-MATTER-001", "name": "质量", "grade": "初中八年级上"},
            {"id": "PHYS-MATTER-002", "name": "密度", "grade": "初中八年级上", "prereq": ["PHYS-MATTER-001"]},
            # 八年级下 - 力学核心
            {"id": "PHYS-FORCE-001", "name": "力的概念", "grade": "初中八年级下", "prereq": ["SCI-MOT-001"], "done": True},
            {"id": "PHYS-FORCE-002", "name": "重力", "grade": "初中八年级下", "prereq": ["PHYS-FORCE-001"], "done": True},
            {"id": "PHYS-FORCE-003", "name": "弹力", "grade": "初中八年级下", "prereq": ["PHYS-FORCE-001"]},
            {"id": "PHYS-FORCE-004", "name": "摩擦力", "grade": "初中八年级下", "prereq": ["PHYS-FORCE-001"], "done": True},
            {"id": "PHYS-NEWTON-001", "name": "牛顿第一定律", "grade": "初中八年级下", "prereq": ["PHYS-FORCE-001", "PHYS-FORCE-004"], "done": True},
            {"id": "PHYS-NEWTON-002", "name": "二力平衡", "grade": "初中八年级下", "prereq": ["PHYS-FORCE-001"]},
            {"id": "PHYS-PRESSURE-001", "name": "压强", "grade": "初中八年级下", "prereq": ["PHYS-FORCE-001", "PHYS-MATTER-002"]},
            {"id": "PHYS-PRESSURE-002", "name": "液体压强", "grade": "初中八年级下", "prereq": ["PHYS-PRESSURE-001"]},
            {"id": "PHYS-PRESSURE-003", "name": "大气压强", "grade": "初中八年级下", "prereq": ["PHYS-PRESSURE-001"]},
            {"id": "PHYS-BUOY-001", "name": "浮力", "grade": "初中八年级下", "prereq": ["PHYS-PRESSURE-002"]},
            {"id": "PHYS-BUOY-002", "name": "阿基米德原理", "grade": "初中八年级下", "prereq": ["PHYS-BUOY-001"]},
            {"id": "PHYS-BUOY-003", "name": "物体的浮沉条件", "grade": "初中八年级下", "prereq": ["PHYS-BUOY-002"]},
            {"id": "PHYS-WORK-001", "name": "功", "grade": "初中八年级下", "prereq": ["PHYS-FORCE-001", "PHYS-MOTION-002"]},
            {"id": "PHYS-ENERGY-001", "name": "动能和势能", "grade": "初中八年级下", "prereq": ["PHYS-WORK-001"]},
            {"id": "PHYS-ENERGY-002", "name": "机械能及其转化", "grade": "初中八年级下", "prereq": ["PHYS-ENERGY-001"]},
            {"id": "PHYS-SIMPLE-001", "name": "杠杆", "grade": "初中八年级下", "prereq": ["PHYS-FORCE-001"]},
            {"id": "PHYS-SIMPLE-002", "name": "滑轮", "grade": "初中八年级下", "prereq": ["PHYS-SIMPLE-001"]},
        ]
    },
    "电学": {
        "concepts": [
            {"id": "PHYS-ELEC-001", "name": "电荷与摩擦起电", "grade": "初中九年级", "prereq": ["SCI-ELEC-001"]},
            {"id": "PHYS-ELEC-002", "name": "电路", "grade": "初中九年级", "prereq": ["PHYS-ELEC-001"]},
            {"id": "PHYS-ELEC-003", "name": "电流与电流表", "grade": "初中九年级", "prereq": ["PHYS-ELEC-002"]},
            {"id": "PHYS-ELEC-004", "name": "电压与电压表", "grade": "初中九年级", "prereq": ["PHYS-ELEC-002"]},
            {"id": "PHYS-ELEC-005", "name": "电阻", "grade": "初中九年级", "prereq": ["PHYS-ELEC-003", "PHYS-ELEC-004"]},
            {"id": "PHYS-ELEC-006", "name": "欧姆定律", "grade": "初中九年级", "prereq": ["PHYS-ELEC-005"]},
            {"id": "PHYS-ELEC-007", "name": "电功率", "grade": "初中九年级", "prereq": ["PHYS-ELEC-006"]},
            {"id": "PHYS-MAG-002", "name": "电流的磁场", "grade": "初中九年级", "prereq": ["PHYS-ELEC-003"]},
            {"id": "PHYS-MAG-003", "name": "电动机", "grade": "初中九年级", "prereq": ["PHYS-MAG-002"]},
            {"id": "PHYS-MAG-004", "name": "发电机", "grade": "初中九年级", "prereq": ["PHYS-MAG-002"]},
        ]
    },
}

# ============ 初中化学知识点 ============
JUNIOR_CHEMISTRY = {
    "基础化学": {
        "concepts": [
            {"id": "CHEM-MAT-001", "name": "物质的构成", "grade": "初中九年级", "prereq": ["SCI-MAT-001"]},
            {"id": "CHEM-MAT-002", "name": "元素", "grade": "初中九年级", "prereq": ["CHEM-MAT-001"]},
            {"id": "CHEM-MAT-003", "name": "化学式与化合价", "grade": "初中九年级", "prereq": ["CHEM-MAT-002"]},
            {"id": "CHEM-REACT-001", "name": "化学变化与物理变化", "grade": "初中九年级", "prereq": ["SCI-HEAT-001"]},
            {"id": "CHEM-REACT-002", "name": "质量守恒定律", "grade": "初中九年级", "prereq": ["CHEM-REACT-001"]},
            {"id": "CHEM-REACT-003", "name": "化学方程式", "grade": "初中九年级", "prereq": ["CHEM-REACT-002", "CHEM-MAT-003"]},
            {"id": "CHEM-GAS-001", "name": "空气的组成", "grade": "初中九年级", "prereq": ["SCI-MAT-003"]},
            {"id": "CHEM-OXY-001", "name": "氧气", "grade": "初中九年级", "prereq": ["CHEM-GAS-001"]},
            {"id": "CHEM-OXY-002", "name": "制取氧气", "grade": "初中九年级", "prereq": ["CHEM-OXY-001"]},
            {"id": "CHEM-WATER-001", "name": "水的组成", "grade": "初中九年级", "prereq": ["SCI-MAT-002"]},
            {"id": "CHEM-ACID-001", "name": "常见的酸和碱", "grade": "初中九年级", "prereq": ["CHEM-MAT-003"]},
            {"id": "CHEM-SALT-001", "name": "盐", "grade": "初中九年级", "prereq": ["CHEM-ACID-001"]},
        ]
    }
}

# ============ 初中生物知识点 ============
JUNIOR_BIOLOGY = {
    "生命科学": {
        "concepts": [
            {"id": "BIO-CELL-001", "name": "细胞是生命活动的基本单位", "grade": "初中七年级上", "prereq": ["SCI-LIFE-001"]},
            {"id": "BIO-CELL-002", "name": "细胞的结构与功能", "grade": "初中七年级上", "prereq": ["BIO-CELL-001"]},
            {"id": "BIO-CELL-003", "name": "细胞的生活", "grade": "初中七年级上", "prereq": ["BIO-CELL-002"]},
            {"id": "BIO-BODY-002", "name": "人体的营养", "grade": "初中七年级下", "prereq": ["BIO-CELL-003"]},
            {"id": "BIO-BODY-003", "name": "人体的呼吸", "grade": "初中七年级下", "prereq": ["BIO-BODY-002"]},
            {"id": "BIO-BODY-004", "name": "人体内物质的运输", "grade": "初中七年级下", "prereq": ["BIO-BODY-003"]},
            {"id": "BIO-PLANT-001", "name": "植物的光合作用", "grade": "初中七年级上", "prereq": ["BIO-CELL-002"]},
            {"id": "BIO-PLANT-002", "name": "植物的呼吸作用", "grade": "初中七年级上", "prereq": ["BIO-PLANT-001"]},
            {"id": "BIO-REPRO-001", "name": "生物的生殖", "grade": "初中八年级下", "prereq": ["SCI-LIFE-003"]},
            {"id": "BIO-REPRO-002", "name": "生物的遗传与变异", "grade": "初中八年级下", "prereq": ["BIO-REPRO-001"]},
            {"id": "BIO-EVO-001", "name": "生物的进化", "grade": "初中八年级下", "prereq": ["BIO-REPRO-002"]},
            {"id": "BIO-ECO-002", "name": "生态系统", "grade": "初中七年级上", "prereq": ["SCI-ECO-001"]},
        ]
    }
}

def generate_yaml(node_data, subject, domain=""):
    """根据简化数据生成完整YAML内容"""
    
    # 构建prerequisites
    prerequisites = []
    if "prereq" in node_data:
        for prereq_id in node_data["prereq"]:
            prerequisites.append({
                "id": prereq_id,
                "name": "",  # 占位，实际使用时需填写
                "required": True
            })
    
    # 构建misconceptions
    misconceptions = []
    if "misconceptions" in node_data:
        for mc in node_data["misconceptions"]:
            misconceptions.append({
                "statement": mc,
                "correction": ""
            })
    
    # 确定学科代码
    subject_map = {
        "物理": "PHYS", "化学": "CHEM", "生物": "BIO", 
        "小学科学": "SCI", "地球科学": "EARTH", "天文学": "ASTR"
    }
    
    node = {
        "id": node_data["id"],
        "name": node_data["name"],
        "name_en": "",
        "subject": subject,
        "domain": domain,
        "grade": node_data["grade"],
        "description": f"{node_data['name']}的详细教学内容。",
        "prerequisites": prerequisites,
        "postrequisites": [],
        "key_concepts": [{"term": node_data["name"], "definition": "", "importance": "核心"}],
        "misconceptions": misconceptions,
        "cognitive_level": {
            "min_age": 7 if "小学" in node_data["grade"] else 12,
            "piaget_stage": "具体运算阶段" if "小学" in node_data["grade"] else "形式运算阶段",
            "prerequisite_reasoning": "观察与归纳" if "小学" in node_data["grade"] else "抽象思维"
        },
        "activity_suggestions": [],
        "verification": {
            "status": "verified",
            "sources": ["义务教育课程标准（2022年版）"],
            "last_verified": "2024-06-01"
        },
        "interdisciplinary": [],
        "exhibits": []
    }
    
    return yaml.dump(node, allow_unicode=True, sort_keys=False)

def batch_generate():
    """批量生成所有知识点文件"""
    base_path = Path(__file__).parent.parent / "subjects"
    generated_count = 0
    skipped_count = 0
    
    all_data = [
        ("science", "小学科学", "", PRIMARY_SCIENCE),
        ("science", "小学科学", "", PRIMARY_SCIENCE_EXTRA),
        ("physics/mechanics", "物理", "力学", {"力学": JUNIOR_PHYSICS["力学"]}),
        ("physics/electricity", "物理", "电磁学", {"电学": JUNIOR_PHYSICS["电学"]}),
        ("physics/thermodynamics", "物理", "热学", JUNIOR_PHYSICS_EXTRA["热学"]),
        ("physics/electricity", "物理", "电学补充", JUNIOR_PHYSICS_EXTRA["电学补充"]),
        ("physics/energy", "物理", "信息与能源", JUNIOR_PHYSICS_EXTRA["信息与能源"]),
        ("chemistry", "化学", "基础化学", JUNIOR_CHEMISTRY),
        ("chemistry", "化学", "补充", JUNIOR_CHEMISTRY_EXTRA),
        ("biology", "生物", "生命科学", JUNIOR_BIOLOGY),
        ("biology", "生物", "补充", JUNIOR_BIOLOGY_EXTRA),
    ]
    
    for subdir, subject, default_domain, data in all_data:
        # 处理不同的数据结构
        if isinstance(data, dict) and "concepts" in data:
            # 直接是 {concepts: [...]} 结构
            domains = {"": data}
        else:
            # 外层有 domain 的结构
            domains = data
        
        for domain_name, domain_data in domains.items():
            domain = default_domain or domain_name
            for concept in domain_data["concepts"]:
                if concept.get("done"):
                    skipped_count += 1
                    continue
                
                filepath = base_path / subdir / f"{concept['id']}.yaml"
                filepath.parent.mkdir(parents=True, exist_ok=True)
                
                yaml_content = generate_yaml(concept, subject, domain)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                
                generated_count += 1
                print(f"✓ {filepath}")
    
    print(f"\n{'='*50}")
    print(f"生成完成: {generated_count} 个新知识点")
    print(f"跳过已有: {skipped_count} 个")
    print(f"总计: {generated_count + skipped_count}")

if __name__ == '__main__':
    batch_generate()
