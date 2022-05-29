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


# This algorithm does not change the order of the sprites (so no "scrambling" of sprites)
# but at the cost of being *slightly* less space-efficient (so you get a slightly bigger spritesheet)
class OrderedPacker:
    def __init__(self):
        self.blocks = None
        self.root = None # not actually a root but named so for consistency

    def fit(self, blocks):
        self.blocks = blocks
        
        blocks_per_row = int(self._get_blocks_per_row_estimate())
        blocks_matrix = []
        for i in range(len(self.blocks)//blocks_per_row + 1):
            blocks_matrix.append( self.blocks[i*blocks_per_row:(i+1)*blocks_per_row] )
        
        if blocks_matrix[-1] == []:
            blocks_matrix = blocks_matrix[:-1]
        
        final_w = self._get_final_width(blocks_matrix)
        final_h = self._get_final_height(blocks_matrix)

        self.root = {
            'w': final_w,
            'h': final_h
        }

        curr_x = 0
        curr_y = 0
        max_heights = [ max([b["h"] for b in row]) for row in blocks_matrix ]

        for i, row in enumerate(blocks_matrix):
            for bl in row:
                bl["fit"] = {
                    'x': curr_x,
                    'y': curr_y
                }
                curr_x += bl["w"]
            curr_y += max_heights[i]
            curr_x = 0


    def _get_blocks_per_row_estimate(self):
        tot_area = sum([ x["w"]*x["h"] for x in self.blocks ])
        estimated_sidelen = tot_area**0.5
        avg_width = self._get_total_width()/len(self.blocks)
        return estimated_sidelen // avg_width

    def _get_total_width(self):
        return sum([ x["w"] for x in self.blocks ])
    
    def _get_final_width(self, rows):
        # maximum value of total width among all the rows
        row_sums = [ sum([b["w"] for b in row]) for row in rows ]
        return max(row_sums)
    
    def _get_final_height(self, rows):
        # sum of the maximum heights of each row
        max_heights = [ max([b["h"] for b in row]) for row in rows ]
        return sum(max_heights)