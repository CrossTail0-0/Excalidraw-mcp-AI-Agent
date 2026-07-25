import json
from ..prompts.excalidraw import EXCALIDRAW_PROMPT



def excalidraw_agent(
    state,
    llm
):
    
    import json

    def compress_excalidraw_docs(raw_docs) -> str:
        if isinstance(raw_docs, (str, bytes, bytearray)):
            try:
                parsed = json.loads(raw_docs)
            except json.JSONDecodeError:
                return raw_docs
        else:
            parsed = raw_docs  # already a list/dict

        if isinstance(parsed, list):
            # adjust based on actual shape — likely a list of element-type dicts
            compact = [
                {
                    "type": item.get("type"),
                    "required": item.get("required", []),
                    "properties": list(item.get("properties", {}).keys())
                }
                for item in parsed
                if isinstance(item, dict)
            ]
            return json.dumps(compact, separators=(",", ":"))

        if isinstance(parsed, dict):
            compact = {
                k: {"required": v.get("required", []), "properties": list(v.get("properties", {}).keys())}
                for k, v in parsed.items()
            }
            return json.dumps(compact, separators=(",", ":"))

        return str(parsed)
    

    compressed_docs = compress_excalidraw_docs(state["excalidraw_docs"])

    prompt = EXCALIDRAW_PROMPT.substitute(

        docs=compressed_docs,

        concept=state["concept"],

        layout=state["layout_plan"]

    )
    print(prompt)

    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )

    print("Excalidraw Agent Response:", response)
    print("Updating state with new elements...")
    state["elements"] = json.loads(response)


    return state