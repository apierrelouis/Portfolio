class Node:
    def __init__(self, key):
        self.key = key
        self.values = []
        self.left = None
        self.right = None

    def __len__(self):
        size = len(self.values)
        if self.left != None:
            size += len(self.left.values)
        if self.right != None:
            size += len(self.right.values)
        return size   
    
    def lookup(self, key):
        if key == self.key:
            return self.values
        if key < self.key and self.left != None:
            return self.left.lookup(key)
        if key > self.key and self.right != None:
            return self.right.lookup(key)
        return []
    '''
    lookup method (takes key)
    if key matches my key, return my values
    if key is less than my key and I have a left child
        call lookup on my left child and return what it returns
    if key is greater than my key and I have a right child
        call lookup on my right child and return what it returns
    otherwise return an empty list
    '''
    
        
class BST:
    def __init__(self):
        self.root = None

    def add(self, key, val):
        if self.root == None:
            self.root = Node(key)
        curr = self.root
        while True:
            if key < curr.key:
                # go left
                if curr.left == None:
                    curr.left = Node(key)
                curr = curr.left
            elif key > curr.key:
                # go right
                if curr.right == None:
                    curr.right = Node(key)
                curr = curr.right
            else:
                # found it!
                assert curr.key == key
                break
        curr.values.append(val)
        
    def __dump(self, node):
        if node == None:
            return
        self.__dump(node.right)            # 1
        print(node.key, ":", node.values)  # 2
        self.__dump(node.left)             # 3

    def dump(self):
        self.__dump(self.root)
        
    def __getitem__(self, key):
        return Node.lookup(self.root, key)
    
    def height(self, node):
        """
        Calculates height of the BST.
        Height: the number of edges on the longest root-to-leaf path
        """
        if node == None:
            return -1
        
        left_height = self.height(node.left)
        right_height = self.height(node.right)

        return max(left_height, right_height) + 1
    
    def size(self, node):
        '''
        Calculates Length/Size of BST
        Size: Number of Nodes in tree
        '''
        if node == None:
            return 0
        else:
            return self.size(node.left) + self.size(node.right) + 1
        
    def leaves(self, node):
        '''
        Calculates number of leaves
        Number of nodes with no children
        '''
        if node == None:
            return 0
        
        if node.left == None and node.right == None:
            return 1
        else:
            return self.leaves(node.left) + self.leaves(node.right)
        
    def tolist(self, node, result=None):
        '''
        Creates a list of the BST keys in descending key value
        '''
        if node == None:
            return []
        
        if result == None:
            result = []
        
        if node.right != None:
            self.tolist(node.right, result)
        result.append(node.key)
        if node.left != None:
            self.tolist(node.left, result)
        
        return result