# Packing Algorithm based on https://github.com/jakesgordon/bin-packing/blob/master/js/packer.growing.js
# converted to python
# By (Jake Gordon)[https://github.com/jakesgordon]
class GrowingPacker:
    def __init__(self):
        self.root = None

    def fit(self, blocks):
        num_blocks = len(blocks)
        w = blocks[0].get("w", 0) if num_blocks > 0 else 0
        h = blocks[0].get("h", 0) if num_blocks > 0 else 0
        self.root = { "x":0, "y":0, "w":w, "h":h }
        for block in blocks:
            node = self.find_node(self.root, block.get("w", 0), block.get("h", 0))
            if node:
                block["fit"] = self.split_node(node, block.get("w", 0), block.get("h", 0))
            else:
                block["fit"] = self.grow_node(block.get("w", 0), block.get("h", 0))
    
    def find_node(self, root, w, h):
        if root.get("used"):
            return self.find_node(root.get("right"), w, h) or self.find_node(root.get("down"), w, h)
        elif w <= root.get("w", 0) and h <= root.get("h", 0):
            return root
        else:
            return None
    
    def split_node(self, node, w, h):
        node["used"] = True
        node['down'] = { "x": node.get("x"), "y": node.get("y") + h, "w": node.get("w"), "h":node.get("h") - h }
        node['right'] = { "x": node.get("x") + w, "y": node.get("y"), "w": node.get("w") - w, "h": h }
        return node
    
    def grow_node(self, w, h):
        canGrowDown = (w <= self.root.get("w"))
        canGrowRight = (h <= self.root.get("h"))

        shouldGrowRight = canGrowRight and (self.root.get("h") >= (self.root.get("w") + w))
        shouldGrowDown = canGrowDown and (self.root.get("w") >= (self.root.get("h") + h))

        if shouldGrowRight:
            return self.grow_right(w, h)
        elif shouldGrowDown:
            return self.grow_down(w, h)
        elif canGrowRight:
            return self.grow_right(w, h)
        elif canGrowDown:
            return self.grow_down(w, h)
        else:
            return None
    
    def grow_right(self, w, h):
        self.root = {
            "used": True, 
            "x":0, 
            "y":0, 
            "w":self.root.get("w")+w,
            "h":self.root.get("h"),
            "down":self.root,
            "right": { "x": self.root.get("w"), "y":0, "w":w, "h":self.root.get("h") }
        }
        node = self.find_node(self.root, w, h)
        if node:
            return self.split_node(node, w, h)
        else:
            return None

    def grow_down(self, w, h):
        self.root = {
            "used": True, 
            "x":0, 
            "y":0, 
            "w":self.root.get("w"),
            "h":self.root.get("h") + h,
            "down": { "x": 0, "y": self.root.get("h"), "w": self.root.get("w"), "h": h },
            "right": self.root
        }
        node = self.find_node(self.root, w, h)
        if node:
            return self.split_node(node, w, h)
        else:
            return None