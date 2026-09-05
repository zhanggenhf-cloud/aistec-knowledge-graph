#!/usr/bin/env python3
"""
自动生成交互式知识图谱可视化
从YAML文件读取数据并生成D3.js可视化HTML
"""

import yaml
import json
from pathlib import Path

def load_knowledge_graph(base_path):
    """加载所有知识点YAML文件"""
    nodes = []
    links = []
    node_map = {}
    
    for yaml_file in sorted(base_path.rglob("*.yaml")):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'id' not in data:
            continue
        
        # 确定学科分组
        subject = data.get('subject', '')
        group = 1
        if '小学科学' in subject:
            group = 1
        elif '物理' in subject:
            group = 2
        elif '化学' in subject:
            group = 3
        elif '生物' in subject:
            group = 4
        
        node = {
            "id": data['id'],
            "name": data['name'],
            "subject": subject,
            "grade": data.get('grade', ''),
            "group": group,
            "isCore": data['id'] in ['PHYS-FORCE-001', 'PHYS-NEWTON-001', 'SCI-MOT-001']
        }
        nodes.append(node)
        node_map[data['id']] = node
        
        # 提取前置关系
        for prereq in data.get('prerequisites', []):
            prereq_id = prereq.get('id', '')
            if prereq_id:
                links.append({
                    "source": prereq_id,
                    "target": data['id']
                })
    
    return nodes, links

def generate_html(nodes, links, output_path):
    """生成D3.js可视化HTML"""
    
    # 序列化数据
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    links_json = json.dumps(links, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AISTEC 知识图谱可视化 ({len(nodes)} 节点)</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e27;
            color: #fff;
            overflow: hidden;
        }}
        #graph {{ width: 100vw; height: 100vh; }}
        .node {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .node:hover {{ filter: brightness(1.3); }}
        .node-circle {{
            stroke-width: 2px;
            stroke: rgba(255,255,255,0.3);
        }}
        .node-label {{
            font-size: 10px;
            fill: #fff;
            text-anchor: middle;
            pointer-events: none;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        }}
        .link {{
            stroke-opacity: 0.4;
            stroke-width: 1px;
        }}
        .link.highlighted {{
            stroke-opacity: 1;
            stroke-width: 3px;
        }}
        #info-panel {{
            position: fixed;
            top: 20px;
            right: 20px;
            width: 320px;
            background: rgba(16, 20, 40, 0.95);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            display: none;
            max-height: 80vh;
            overflow-y: auto;
        }}
        #info-panel h2 {{
            font-size: 18px;
            margin-bottom: 10px;
            color: #64b5f6;
        }}
        #info-panel .field {{
            margin: 8px 0;
            font-size: 13px;
        }}
        #info-panel .field-label {{
            color: #8892b0;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        #info-panel .field-value {{
            color: #ccd6f6;
            margin-top: 2px;
        }}
        #controls {{
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(16, 20, 40, 0.95);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 15px;
            backdrop-filter: blur(10px);
        }}
        #controls h3 {{
            font-size: 14px;
            margin-bottom: 10px;
            color: #64b5f6;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 12px;
        }}
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        #search-box {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(16, 20, 40, 0.95);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 10px 15px;
            display: flex;
            gap: 10px;
        }}
        #search-input {{
            background: transparent;
            border: none;
            color: #fff;
            outline: none;
            width: 200px;
        }}
        #search-input::placeholder {{ color: #8892b0; }}
        #stats {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(16, 20, 40, 0.95);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 12px;
            color: #8892b0;
        }}
    </style>
</head>
<body>
    <div id="graph"></div>
    
    <div id="controls">
        <h3>学科分类 (共 {len(nodes)} 节点)</h3>
        <div class="legend-item">
            <div class="legend-color" style="background: #4caf50;"></div>
            <span>小学科学 ({sum(1 for n in nodes if n['group']==1)})</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #2196f3;"></div>
            <span>初中物理 ({sum(1 for n in nodes if n['group']==2)})</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #ff9800;"></div>
            <span>初中化学 ({sum(1 for n in nodes if n['group']==3)})</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #e91e63;"></div>
            <span>初中生物 ({sum(1 for n in nodes if n['group']==4)})</span>
        </div>
    </div>
    
    <div id="info-panel">
        <h2 id="info-title">概念详情</h2>
        <div class="field">
            <div class="field-label">ID</div>
            <div class="field-value" id="info-id"></div>
        </div>
        <div class="field">
            <div class="field-label">学科</div>
            <div class="field-value" id="info-subject"></div>
        </div>
        <div class="field">
            <div class="field-label">年级</div>
            <div class="field-value" id="info-grade"></div>
        </div>
        <div class="field">
            <div class="field-label">前置知识</div>
            <div class="field-value" id="info-prereq"></div>
        </div>
    </div>
    
    <div id="search-box">
        <input type="text" id="search-input" placeholder="搜索知识点...">
    </div>
    
    <div id="stats">
        节点: {len(nodes)} | 连接: {len(links)}
    </div>

    <script>
        const graphData = {{
            nodes: {nodes_json},
            links: {links_json}
        }};

        const colorMap = {{
            1: '#4caf50',
            2: '#2196f3',
            3: '#ff9800',
            4: '#e91e63'
        }};

        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        const g = svg.append("g");
        
        svg.call(d3.zoom()
            .extent([[0, 0], [width, height]])
            .scaleExtent([0.05, 4])
            .on("zoom", ({{transform}}) => {{
                g.attr("transform", transform);
            }}));
        
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(80))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(30));
        
        const link = g.append("g")
            .selectAll("line")
            .data(graphData.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke", "#64b5f6");
        
        const node = g.append("g")
            .selectAll("g")
            .data(graphData.nodes)
            .join("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        node.append("circle")
            .attr("class", "node-circle")
            .attr("r", d => d.isCore ? 20 : 12)
            .attr("fill", d => colorMap[d.group])
            .attr("stroke", d => d.isCore ? "#ff5252" : "rgba(255,255,255,0.3)")
            .attr("stroke-width", d => d.isCore ? 3 : 2);
        
        node.append("text")
            .attr("class", "node-label")
            .attr("dy", d => d.isCore ? 30 : 22)
            .text(d => d.name);
        
        node.on("click", (event, d) => {{
            showInfo(d);
            highlightPath(d);
        }});
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        function showInfo(d) {{
            document.getElementById('info-panel').style.display = 'block';
            document.getElementById('info-title').textContent = d.name;
            document.getElementById('info-id').textContent = d.id;
            document.getElementById('info-subject').textContent = d.subject;
            document.getElementById('info-grade').textContent = d.grade;
            
            const prereqs = graphData.links
                .filter(l => l.target.id === d.id)
                .map(l => l.source.name);
            document.getElementById('info-prereq').textContent = 
                prereqs.length > 0 ? prereqs.join('、') : '无';
        }}
        
        function highlightPath(selectedNode) {{
            link.classed('highlighted', false);
            
            const connectedLinks = graphData.links.filter(
                l => l.source.id === selectedNode.id || l.target.id === selectedNode.id
            );
            
            link.filter(d => connectedLinks.includes(d))
                .classed('highlighted', true);
        }}
        
        document.getElementById('search-input').addEventListener('input', (e) => {{
            const term = e.target.value.toLowerCase();
            if (!term) {{
                node.style('opacity', 1);
                link.style('opacity', 1);
                return;
            }}
            
            const matched = graphData.nodes.filter(n => 
                n.name.toLowerCase().includes(term) || 
                n.id.toLowerCase().includes(term)
            );
            
            node.style('opacity', d => matched.includes(d) ? 1 : 0.1);
            link.style('opacity', 0.05);
        }});
        
        svg.on("click", (event) => {{
            if (event.target.tagName === 'svg') {{
                document.getElementById('info-panel').style.display = 'none';
                link.classed('highlighted', false);
            }}
        }});
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ 生成交互式可视化: {output_path}")
    print(f"  节点: {len(nodes)}, 连接: {len(links)}")

if __name__ == '__main__':
    base_path = Path(__file__).parent.parent / "subjects"
    output_path = Path(__file__).parent.parent / "visualizations" / "interactive-graph.html"
    
    nodes, links = load_knowledge_graph(base_path)
    generate_html(nodes, links, output_path)
