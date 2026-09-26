import json


class Node:
    __slots__ = ("depth", "key", "value", "children")

    def __init__(self, depth: int, key: str, value):
        self.depth = depth
        self.key = key
        self.value = value   # None if the line has no bracketed text
        self.children: list["Node"] = []


class TemplateLoader:

    def _parseLine(self, line: str):
        """Return (depth, key, value) for one line of the template."""
        stripped = line.rstrip("\n").rstrip("\r")
        depth = len(stripped) - len(stripped.lstrip("\t"))
        rest = stripped.lstrip("\t")

        idx = rest.find("[")
        if idx == -1:
            key = rest.strip()
            value = None
        else:
            key = rest[:idx].strip()
            value = rest[idx:].strip()

        return depth, key, value

    def _buildTree(self, lines: list[str]) -> Node:
        """Build a tree of Nodes from raw template lines, using tab-depth for nesting."""
        root = Node(depth=-1, key="__root__", value=None)
        stack = [root]

        for raw_line in lines:
            if not raw_line.strip():
                continue  # skip blank lines

            depth, key, value = self._parseLine(raw_line)
            if not key:
                continue  # skip lines that are only whitespace/brackets

            node = Node(depth, key, value)

            # pop back to the correct parent level
            while stack[-1].depth >= depth:
                stack.pop()

            stack[-1].children.append(node)
            stack.append(node)

        print(root)
        return root

    def _nodeToJson(self, node: Node):
        """Recursively convert a Node into a plain dict/str for json.dumps."""
        if not node.children:
            return node.value if node.value is not None else ""

        result = {}
        if node.value is not None:
            result["_description"] = node.value

        for child in node.children:
            result[child.key] = self._nodeToJson(child)

        return result

    def unpackTemplateFile(self, filePath: str) -> object:
        converted_file: object = None

        try:
            with open(filePath, "r", encoding="utf-8") as template:
                lines = template.readlines()

            root = self._buildTree(lines)
            structured = {child.key: self._nodeToJson(child) for child in root.children}

            converted_file = json.dumps(structured, indent=4, ensure_ascii=False)

        except Exception as e:
            print(e)

        return converted_file