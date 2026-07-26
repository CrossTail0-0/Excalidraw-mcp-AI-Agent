"""
    The goal is to build the diagram elements list.
    DATA:
        - components contains node ids and the text that should be inside them (label).
        - components contains connections (from node id to another node id) which is used for arrows
        - components contains groups which are used for colors
        - layout contains layout which has positions x and y
        - design contains which shape is the node (rectangle, diamond, ellipse)

    RULES:
        - nodes constants: "width": 160,"height": 80, "fillStyle": "solid", "strokeColor": "#1976d2","strokeWidth": 2,"roundness": {"type": 3}
        - text is always bound to its node
        - Text in nodes: fontSize=20, fontFamily="Virgil", textAlign="center", verticalAlign="middle"
        - Text position: x=parent.x+20, y=parent.y+parent.height/2-15, width=parent.width-40
        - nodes in the same groups should have the same color  (chosen randomly from colors)
        - Arrow position: 
            source = {"x": 400, "y": 50, "width": 160, "height": 80}
            target = {"x": 250, "y": 220, "width": 160, "height": 80}
            def calculate_arrow_between_nodes(source, target):
                
                # Calculate centers
                source_center_x = source["x"] + source["width"] / 2
                source_center_y = source["y"] + source["height"] / 2
                target_center_x = target["x"] + target["width"] / 2
                target_center_y = target["y"] + target["height"] / 2
                
                # Determine relative direction
                dx = target_center_x - source_center_x
                dy = target_center_y - source_center_y
                
                # Arrow starts from edge of source, in direction of target
                if abs(dy) > abs(dx):
                    # Primarily vertical
                    if dy > 0:
                        # Source bottom → Target top
                        arrow_x = source["x"] + source["width"] / 2
                        arrow_y = source["y"] + source["height"]
                        points = [[0, 0], [dx, dy - source["height"]/2 - target["height"]/2]]
                    else:
                        # Source top → Target bottom
                        arrow_x = source["x"] + source["width"] / 2
                        arrow_y = source["y"]
                        points = [[0, 0], [dx, dy + source["height"]/2 + target["height"]/2]]
                else:
                    # Primarily horizontal
                    if dx > 0:
                        # Source right → Target left
                        arrow_x = source["x"] + source["width"]
                        arrow_y = source["y"] + source["height"] / 2
                        points = [[0, 0], [dx - source["width"]/2 - target["width"]/2, dy]]
                    else:
                        # Source left → Target right
                        arrow_x = source["x"]
                        arrow_y = source["y"] + source["height"] / 2
                        points = [[0, 0], [dx + source["width"]/2 + target["width"]/2, dy]]
                
                return {
                    "x": arrow_x,
                    "y": arrow_y,
                    "points": points,
                    "startBinding": {"elementId": source["id"], "focus": 0, "gap": 5},
                    "endBinding": {"elementId": target["id"], "focus": 0, "gap": 5}
                }
    
    SCHEMA:
        [
            {
                "type": "rectangle",
                "id": "client",
                "x": 400,
                "y": 50,
                "width": 160,
                "height": 80,
                "backgroundColor": "#e3f2fd",
                "fillStyle": "solid",
                "strokeColor": "#1976d2",
                "strokeWidth": 2,
                "roundness": {
                "type": 3
                },
                "boundElements": [
                {
                    "id": "text_client",
                    "type": "text"
                }
                ]
            },
            {
                "type": "text",
                "id": "text_client",
                "x": 420,
                "y": 75,
                "width": 120,
                "height": 30,
                "text": "Client",
                "fontSize": 20,
                "fontFamily": "Virgil",
                "textAlign": "center",
                "verticalAlign": "middle",
                "containerId": "client"
            },
            {
                "type": "rectangle",
                "id": "api_gateway",
                "x": 250,
                "y": 220,
                "width": 160,
                "height": 80,
                "backgroundColor": "#fff3e0",
                "fillStyle": "solid",
                "strokeColor": "#f57c00",
                "strokeWidth": 2,
                "roundness": {
                "type": 3
                },
                "boundElements": [
                {
                    "id": "text_api_gateway",
                    "type": "text"
                }
                ]
            },
            {
                "type": "text",
                "id": "text_api_gateway",
                "x": 270,
                "y": 245,
                "width": 120,
                "height": 30,
                "text": "API Gateway",
                "fontSize": 20,
                "fontFamily": "Virgil",
                "textAlign": "center",
                "verticalAlign": "middle",
                "containerId": "api_gateway"
            },
            {
                "type": "arrow",
                "id": "arrow_client_to_gateway",
                "x": 480,
                "y": 130,
                "points": [
                    [0, 0],
                    [0, 90]
                ],
                "strokeColor": "#546e7a",
                "strokeWidth": 2,
                "startBinding": {
                "elementId": "client",
                "focus": 0,
                "gap": 5
                },
                "endBinding": {
                "elementId": "api_gateway",
                "focus": 0,
                "gap": 5
                }
            }
            ]

    """

import json
import random



def excalidraw_agent(state, llm=None):
    """
    Build Excalidraw elements programmatically from components, layout, and design.
    No LLM needed — pure deterministic construction.
    """
    
    components = state["components"]  # {"nodes": [...], "connections": [...], "groups": [...]}
    layout = state["layout"]          # {"diagram_type": "", "direction": "", "nodes": [...]}
    design = state["design"]          # {"nodes": [{"id": "", "type": ""}, ...]}
    
    # Color palettes for groups (randomly assigned per group)
    COLOR_PALETTES = [
        {"bg": "#e3f2fd", "stroke": "#1976d2"},  # blue
        {"bg": "#fff3e0", "stroke": "#f57c00"},  # orange
        {"bg": "#e8f5e9", "stroke": "#388e3c"},  # green
        {"bg": "#fce4ec", "stroke": "#c2185b"},  # pink
        {"bg": "#f3e5f5", "stroke": "#7b1fa2"},  # purple
        {"bg": "#fff9c4", "stroke": "#fbc02d"},  # yellow
        {"bg": "#e0f2f1", "stroke": "#00796b"},  # teal
        {"bg": "#ede7f6", "stroke": "#4527a0"},  # deep purple
        {"bg": "#fff8e1", "stroke": "#ff8f00"},  # amber
        {"bg": "#f1f8e9", "stroke": "#558b2f"},  # light green
    ]
    
    # Assign colors to groups
    group_colors = {}
    groups = components.get("groups", [])
    
    # Shuffle colors for randomness, but keep it deterministic per session
    available_colors = COLOR_PALETTES.copy()
    random.shuffle(available_colors)
    
    for i, group in enumerate(groups):
        group_name = group["name"]
        group_colors[group_name] = available_colors[i % len(available_colors)]
    
    # Default color for ungrouped nodes
    default_color = {"bg": "#f5f5f5", "stroke": "#9e9e9e"}
    
    # Build lookup maps
    node_map = {n["id"]: n for n in components["nodes"]}
    layout_map = {n["id"]: n for n in layout.get("nodes", layout.get("layout", []))}
    design_map = {n["id"]: n for n in design["nodes"]}
    group_map = {}  # node_id -> group_name
    for group in groups:
        for node_id in group["ids"]:
            group_map[node_id] = group["name"]
    
    elements = []
    used_ids = set()
    
    def make_id(base_id):
        """Ensure unique IDs."""
        return base_id
    
    # ============================================================
    # 1. Generate group container frames (if there are groups)
    # ============================================================
    if groups:
        for group in groups:
            group_name = group["name"]
            group_node_ids = group["ids"]
            
            # Calculate bounding box for all nodes in the group
            group_nodes = [layout_map[nid] for nid in group_node_ids if nid in layout_map]
            if not group_nodes:
                continue
            
            # Find min/max coordinates
            min_x = min(n["x"] for n in group_nodes)
            min_y = min(n["y"] for n in group_nodes)
            max_x = max(n["x"] + 160 for n in group_nodes)  # assume width 160
            max_y = max(n["y"] + 80 for n in group_nodes)   # assume height 80
            
            padding = 40
            frame_x = min_x - padding
            frame_y = min_y - padding - 20  # extra space for label
            frame_width = (max_x - min_x) + (padding * 2)
            frame_height = (max_y - min_y) + (padding * 2) + 20
            
            frame_id = f"frame_{group_name.lower().replace(' ', '_')}"
            text_id = f"text_{frame_id}"
            
            # Frame rectangle
            elements.append({
                "type": "rectangle",
                "id": frame_id,
                "x": frame_x,
                "y": frame_y,
                "width": frame_width,
                "height": frame_height,
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeColor": "#90a4ae",
                "strokeWidth": 1,
                "strokeStyle": "dashed",
                "roundness": None,
                "boundElements": [{"id": text_id, "type": "text"}]
            })
            used_ids.add(frame_id)
            
            # Frame label
            elements.append({
                "type": "text",
                "id": text_id,
                "x": frame_x + 20,
                "y": frame_y + 5,
                "width": frame_width - 40,
                "height": 25,
                "text": group_name,
                "fontSize": 16,
                "fontFamily": "Virgil",
                "textAlign": "center",
                "verticalAlign": "top",
                "containerId": frame_id
            })
            used_ids.add(text_id)
    
    # ============================================================
    # 2. Generate node shapes and text elements
    # ============================================================
    for node in components["nodes"]:
        node_id = node["id"]
        label = node["label"]
        
        # Get layout position
        if node_id not in layout_map:
            continue
        pos = layout_map[node_id]
        x = pos["x"]
        y = pos["y"]
        
        # Get shape type
        shape_type = design_map.get(node_id, {}).get("type", "rectangle")
        
        # Get color based on group
        group_name = group_map.get(node_id)
        if group_name and group_name in group_colors:
            color = group_colors[group_name]
        else:
            color = default_color
        
        # Node dimensions
        width = 160
        height = 80
        
        # Adjust for different shapes
        if shape_type == "diamond":
            width = 160
            height = 100
        elif shape_type == "ellipse":
            width = 140
            height = 80
        
        text_id = f"text_{node_id}"
        
        # Shape element
        shape_element = {
            "type": shape_type,
            "id": node_id,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "backgroundColor": color["bg"],
            "fillStyle": "solid",
            "strokeColor": color["stroke"],
            "strokeWidth": 2,
            "boundElements": [{"id": text_id, "type": "text"}]
        }
        
        # Add roundness for rectangles
        if shape_type == "rectangle":
            shape_element["roundness"] = {"type": 3}
        
        elements.append(shape_element)
        used_ids.add(node_id)
        
        # Text element positioned inside the node
        text_x = x + 20
        text_y = y + (height / 2) - 15
        text_width = width - 40
        
        elements.append({
            "type": "text",
            "id": text_id,
            "x": text_x,
            "y": text_y,
            "width": text_width,
            "height": 30,
            "text": label,
            "fontSize": 20,
            "fontFamily": "Virgil",
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": node_id
        })
        used_ids.add(text_id)
    
    # ============================================================
    # 3. Generate arrow connections
    # ============================================================
    # Track bidirectional connections to offset focus
    connection_pairs = {}
    for conn in components["connections"]:
        key = tuple(sorted([conn["from"], conn["to"]]))
        if key not in connection_pairs:
            connection_pairs[key] = []
        connection_pairs[key].append(conn)
    
    for conn in components["connections"]:
        from_id = conn["from"]
        to_id = conn["to"]
        
        if from_id not in layout_map or to_id not in layout_map:
            continue
        
        source_pos = layout_map[from_id]
        target_pos = layout_map[to_id]
        
        # Get shape types for dimension adjustments
        source_type = design_map.get(from_id, {}).get("type", "rectangle")
        target_type = design_map.get(to_id, {}).get("type", "rectangle")
        
        source_width = 160 if source_type != "ellipse" else 140
        source_height = 100 if source_type == "diamond" else 80
        target_width = 160 if target_type != "ellipse" else 140
        target_height = 100 if target_type == "diamond" else 80
        
        source = {
            "id": from_id,
            "x": source_pos["x"],
            "y": source_pos["y"],
            "width": source_width,
            "height": source_height
        }
        target = {
            "id": to_id,
            "x": target_pos["x"],
            "y": target_pos["y"],
            "width": target_width,
            "height": target_height
        }
        
        # Check if bidirectional
        key = tuple(sorted([from_id, to_id]))
        is_bidirectional = len(connection_pairs.get(key, [])) > 1
        
        # Determine focus offset for bidirectional arrows
        if is_bidirectional:
            # Find index of this connection in the pair
            pair_connections = connection_pairs[key]
            idx = pair_connections.index(conn)
            focus = 0.3 if idx == 0 else -0.3
        else:
            focus = 0
        
        # Calculate arrow position
        arrow = calculate_arrow_between_nodes(source, target, focus)
        
        arrow_id = f"arrow_{from_id}_to_{to_id}"
        # Handle duplicate arrow IDs (bidirectional)
        counter = 1
        base_arrow_id = arrow_id
        while arrow_id in used_ids:
            arrow_id = f"{base_arrow_id}_{counter}"
            counter += 1
        
        elements.append({
            "type": "arrow",
            "id": arrow_id,
            "x": arrow["x"],
            "y": arrow["y"],
            "points": arrow["points"],
            "strokeColor": "#546e7a",
            "strokeWidth": 2,
            "startBinding": arrow["startBinding"],
            "endBinding": arrow["endBinding"]
        })
        used_ids.add(arrow_id)
    
    # ============================================================
    # Store result
    # ============================================================
    state["elements"] = elements
    
    return state




def calculate_arrow_between_nodes(source, target, focus=0):
    """
    Calculate arrow position and points between two nodes.
    
    Args:
        source: {"id": str, "x": float, "y": float, "width": float, "height": float}
        target: {"id": str, "x": float, "y": float, "width": float, "height": float}
        focus: float (-1 to 1) for offsetting the connection point on the edge
    
    Returns:
        dict with x, y, points, startBinding, endBinding
    """
    
    # Calculate centers
    source_center_x = source["x"] + source["width"] / 2
    source_center_y = source["y"] + source["height"] / 2
    target_center_x = target["x"] + target["width"] / 2
    target_center_y = target["y"] + target["height"] / 2
    
    # Determine relative direction
    dx = target_center_x - source_center_x
    dy = target_center_y - source_center_y
    
    # Arrow starts from edge of source, in direction of target
    if abs(dy) > abs(dx):
        # Primarily vertical
        if dy > 0:
            # Source bottom → Target top
            arrow_x = source["x"] + source["width"] / 2
            arrow_y = source["y"] + source["height"]
            points = [[0, 0], [dx, dy - source["height"]/2 - target["height"]/2]]
        else:
            # Source top → Target bottom
            arrow_x = source["x"] + source["width"] / 2
            arrow_y = source["y"]
            points = [[0, 0], [dx, dy + source["height"]/2 + target["height"]/2]]
    else:
        # Primarily horizontal
        if dx > 0:
            # Source right → Target left
            arrow_x = source["x"] + source["width"]
            arrow_y = source["y"] + source["height"] / 2
            points = [[0, 0], [dx - source["width"]/2 - target["width"]/2, dy]]
        else:
            # Source left → Target right
            arrow_x = source["x"]
            arrow_y = source["y"] + source["height"] / 2
            points = [[0, 0], [dx + source["width"]/2 + target["width"]/2, dy]]
    
    return {
        "x": arrow_x,
        "y": arrow_y,
        "points": points,
        "startBinding": {"elementId": source["id"], "focus": focus, "gap": 5},
        "endBinding": {"elementId": target["id"], "focus": focus, "gap": 5}
    }