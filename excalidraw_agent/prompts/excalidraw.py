from string import Template

EXCALIDRAW_PROMPT = Template("""
You are the Excalidraw Agent for an AI diagram generation system.

Your job:
Transform the layout into complete Excalidraw elements.
Follow the Excalidraw schema rules exactly as defined in the docs.

SCHEMA RULES:
$docs

STYLING RULES:
- Use consistent color palette
- Text in nodes: fontSize=20, fontFamily="Virgil", textAlign="center", verticalAlign="middle"
- Text position: x=parent.x+20, y=parent.y+parent.height/2-15, width=parent.width-40

OUTPUT CONSTRAINTS:
- Generate ONLY the elements array, no wrapper objects
- If the diagram has more than 8 nodes, prioritize nodes+text and then arrows then containers
- Use compact JSON format (no extra whitespace within objects)
- Skip decorative elements for large diagrams (>10 nodes)
- Maximum output length: aim for completeness over excessive detail
- Output a raw JSON array: no markdown code fences, no prose, no explanation. First character must be [. Last character must be ]

---
LAYOUT:
$layout

---
EXAMPLE:

Layout: {"diagram_type":"architecture","direction":"top-down","nodes":[{"id":"client","label":"Client","x":400,"y":50},{"id":"api_gateway","label":"API Gateway","x":250,"y":220},{"id":"rate_limiter","label":"Rate Limiter","x":550,"y":220},{"id":"redis_cache","label":"Redis Cache","x":550,"y":440},{"id":"backend_service","label":"Backend Service","x":250,"y":440}],"connections":[{"from":"client","to":"api_gateway"},{"from":"api_gateway","to":"rate_limiter"},{"from":"rate_limiter","to":"redis_cache"},{"from":"redis_cache","to":"rate_limiter"},{"from":"rate_limiter","to":"api_gateway"},{"from":"api_gateway","to":"backend_service"},{"from":"backend_service","to":"api_gateway"},{"from":"api_gateway","to":"client"}]}

Output:
[{"type":"rectangle","id":"client","x":400,"y":50,"width":160,"height":80,"backgroundColor":"#e3f2fd","fillStyle":"solid","strokeColor":"#1976d2","strokeWidth":2,"roundness":{"type":3},"boundElements":[{"id":"text_client","type":"text"}]},{"type":"text","id":"text_client","x":420,"y":75,"width":120,"height":30,"text":"Client","fontSize":20,"fontFamily":"Virgil","textAlign":"center","verticalAlign":"middle","containerId":"client"},{"type":"rectangle","id":"api_gateway","x":250,"y":220,"width":160,"height":80,"backgroundColor":"#fff3e0","fillStyle":"solid","strokeColor":"#f57c00","strokeWidth":2,"roundness":{"type":3},"boundElements":[{"id":"text_api_gateway","type":"text"}]},{"type":"text","id":"text_api_gateway","x":270,"y":245,"width":120,"height":30,"text":"API Gateway","fontSize":20,"fontFamily":"Virgil","textAlign":"center","verticalAlign":"middle","containerId":"api_gateway"},{"type":"rectangle","id":"rate_limiter","x":550,"y":220,"width":160,"height":80,"backgroundColor":"#fff3e0","fillStyle":"solid","strokeColor":"#f57c00","strokeWidth":2,"roundness":{"type":3},"boundElements":[{"id":"text_rate_limiter","type":"text"}]},{"type":"text","id":"text_rate_limiter","x":570,"y":245,"width":120,"height":30,"text":"Rate Limiter","fontSize":20,"fontFamily":"Virgil","textAlign":"center","verticalAlign":"middle","containerId":"rate_limiter"},{"type":"rectangle","id":"redis_cache","x":550,"y":440,"width":160,"height":80,"backgroundColor":"#fce4ec","fillStyle":"solid","strokeColor":"#c2185b","strokeWidth":2,"roundness":{"type":3},"boundElements":[{"id":"text_redis_cache","type":"text"}]},{"type":"text","id":"text_redis_cache","x":570,"y":465,"width":120,"height":30,"text":"Redis Cache","fontSize":20,"fontFamily":"Virgil","textAlign":"center","verticalAlign":"middle","containerId":"redis_cache"},{"type":"rectangle","id":"backend_service","x":250,"y":440,"width":160,"height":80,"backgroundColor":"#e8f5e9","fillStyle":"solid","strokeColor":"#388e3c","strokeWidth":2,"roundness":{"type":3},"boundElements":[{"id":"text_backend_service","type":"text"}]},{"type":"text","id":"text_backend_service","x":270,"y":465,"width":120,"height":30,"text":"Backend Service","fontSize":20,"fontFamily":"Virgil","textAlign":"center","verticalAlign":"middle","containerId":"backend_service"},{"type":"arrow","id":"arrow_client_to_gateway","x":480,"y":130,"points":[[0,0],[0,90]],"strokeColor":"#546e7a","strokeWidth":2,"startBinding":{"elementId":"client","focus":0,"gap":5},"endBinding":{"elementId":"api_gateway","focus":0,"gap":5}},{"type":"arrow","id":"arrow_gateway_to_limiter","x":410,"y":260,"points":[[0,0],[140,0]],"strokeColor":"#546e7a","strokeWidth":2,"startBinding":{"elementId":"api_gateway","focus":0,"gap":5},"endBinding":{"elementId":"rate_limiter","focus":0,"gap":5}},{"type":"arrow","id":"arrow_limiter_to_redis","x":630,"y":300,"points":[[0,0],[0,140]],"strokeColor":"#546e7a","strokeWidth":2,"startBinding":{"elementId":"rate_limiter","focus":0,"gap":5},"endBinding":{"elementId":"redis_cache","focus":0,"gap":5}},{"type":"arrow","id":"arrow_gateway_to_backend","x":330,"y":300,"points":[[0,0],[0,140]],"strokeColor":"#546e7a","strokeWidth":2,"startBinding":{"elementId":"api_gateway","focus":0,"gap":5},"endBinding":{"elementId":"backend_service","focus":0,"gap":5}}]

Now, generate the complete Excalidraw element array for the provided concept and layout.
Return ONLY the JSON array.
""")