"""
Finds the suffix array of a string. Runs in linear time using Ukkonen's algorithm.
Comments assume that you are already familiar with how the algorithm works.
"""

class BranchEndPos:
    """Used to optimise tree results. Used to point to the position a leaf ends at. Useful as all leaves
    will end at the same position"""

    pos = -1

    def increment(self):
        self.pos += 1

class Remainder:
    """
    For handling the remainder easily
    """

    startPos = -1
    endPos = -2

    def isEmpty(self):
        """ If empty. Empty = start > end"""
        return self.startPos > self.endPos

    def set(self,startPos,endPos):
        """ Sets the start and end pos"""
        self.startPos = startPos
        self.endPos = endPos

    def decrease(self, n):
        """
        Decreases remainder by n (from left side).
        Will only do if remainder is not empty
        """
        if not self.isEmpty():
            self.startPos += n

    def increase(self, startPos, endPos):
        """
        Increases the remainder to include the bounds given. If
        isEmpty() then it sets to bounds given, otherwise increases the right bound
        (left bound stays the same)"""

        if self.isEmpty():
            self.startPos = startPos
        
        self.endPos = endPos

    def print(self):
        """For debugging"""
        print("S: ", self.startPos, " E: ", self.endPos)

class Pending:
    """
    For handling pending nodes easily
    """

    old = None
    new = None

    def push(self, new):
        """Adds a new pending"""
        self.new = new

    def pull(self):
        """Returns oldest pending. Pulls the new one forward"""
        old = self.old
        self.old = self.new
        self.new = None
        return old
       
class Node:
    """A node of a tree"""
    start = -1
    endPos = "Unassigned"
    increments = True
    alphabet_size = 128

    suffixLink = None
    father = None # node whose subNodes array this node appears in
    
    nameCounter = [-1]

    def __init__(self, start: int, endPos, father, increments=True):
        self.endPos = endPos
        self.start = start
        self.increments = increments
        self.father = father

        self.subNodes = [None] * self.alphabet_size # Has to be asigned here. Otherwise list will be shared between
        # all class instances

        self.nameCounter[0] += 1
        self.name = self.nameCounter[0] # for debugging purposes


    def getEnd(self):
        if self.increments:
            return self.endPos.pos
        else:
            return self.endPos
        
    def clearSubNodes(self):
        self.subNodes = [None] * self.alphabet_size


    def hasSuffixLink(self):
        return self.suffixLink == None 

def suffixTreeDFSParser(root:Node, traversedLen=0, suffixes=[], suffixIntentionallySet = False):
    """Does DFS on a suffix tree, this finds the correspoding suffix arrray"""

    if suffixIntentionallySet == False:
        suffixes = [] #Python will share the array across all function calls if using a default array value

    isLeaf = True
    
    for node in root.subNodes:

        if node != None: #Traverse branch
            
            #Append
            suffixTreeDFSParser(node, root.getEnd() - root.start + 1 + traversedLen, suffixes, True) # +1 as if start and end are same position it will be 0 length otherwise
            isLeaf = False
        
        else: 
            pass

    if isLeaf:
        suffixes.append(root.getEnd() - root.start + 1 + traversedLen)# Total length of path
    
    return suffixes

def suffixTreeDFS(root:Node, n):
    """Does DFS on a suffix tree"""
    suffixes = suffixTreeDFSParser(root)
    for i in range(len(suffixes)):
        suffixes[i] = n - suffixes[i] # convert length -> position
    return suffixes

def printSuffixTree(root: Node):
    """Debugging function"""
    tree = []

    if root.name == 3:
        pass

    if root.subNodes == [None]*5: #Leaf
        return []

    # Reccursively print branches
    for node in root.subNodes:
        if node == None:
            tree.append(None)
        else:
            if node.suffixLink == None:
                name = "None"

            else:
                name = node.suffixLink.name
                print("SL found", node.name, " to ", name)
            tree.append(f"N{node.name}: {node.start}, {node.getEnd()} {printSuffixTree(node)}, SL:{name}")

    return tree

def splitBranchInMiddle(s: str, root: Node, k: int, endPosPointer: BranchEndPos, currBranchDistTrav:int):
    """Used when  a branch of suffix tree nmust be broken in middle
    s = string you are making a suffix tree out of
    
    k = point of mismatch in the string
    
    j = start of suffix

    root = root of this section of the tree

    k = pos in string of where suffix startt at current branch

    endPosPointer = global leaf endpoint
    
    currBranchDistTrav = how many letters on current branch have been successfuly traversed

    Returns pending node

    """

    # Node to start where old branch started before it gets cut
    oldBranchPrefix = Node(root.start, root.start + currBranchDistTrav - 1, root.father, False)

    # Old branch starts later
    root.start = root.start + currBranchDistTrav

    # Node for new branch
    newBranch = Node(k + currBranchDistTrav, endPosPointer, oldBranchPrefix)

    # Get letters/positions for each new branch to go down
    obLetter = s[root.start]
    obNumber =  ord(obLetter) #which element in array to take up

    nbLetter = s[newBranch.start]
    nbNumber = ord(nbLetter) #which element in array to take up

    # Update root branches
    oldBranchPrefix.subNodes[obNumber] = root
    oldBranchPrefix.subNodes[nbNumber] = newBranch

    # Edit the father of root to point to oldBranchPrefix instead of root
    rootLetter = s[oldBranchPrefix.start]
    rootNumber = ord(rootLetter) #which element in array to take up

    root.father.subNodes[rootNumber] = oldBranchPrefix

    # Father of root is now oldBranchPrefix
    root.father = oldBranchPrefix

    return oldBranchPrefix #pending node

def traverse(s: str, j:int, i:int, currentBranch: Node, remainder: Remainder, endPos: BranchEndPos):
    """
    Traverses the suffix tree with a suffix and makes cuts etc.

    j = start of the suffix 

    i = end of the suffix 

    currentBranch = node of tree to start on

    remainder = remainder of the suffis to traverse

    endPosPointer = global leaf endpoint

    Returns: rule #, new active node, new pending, remainder
    
    """


    if not remainder.isEmpty(): #can skip letters of lastJ so you start at remainder
        j = remainder.startPos

    else:
        j = i #if remainder is empty only try insert one letter only

    activeNode = currentBranch #deepest fully traversed node

    #Start of by going to the end of the current branch (nodes store their letters before them selves) 
    suffixLetter = s[j] #Letter one past end of branch, which you check for matching sub-branches
    suffixLetterNum =  ord(suffixLetter) #which element in array to take up
    
    if currentBranch.subNodes[suffixLetterNum] != None: # if there is a good sub-branch to go down follow it
        activeNode = currentBranch 
        currentBranch = currentBranch.subNodes[suffixLetterNum]

    else: # no good sub-branches to go down, make a new sub branch
        currentBranch.subNodes[suffixLetterNum] = Node(j, endPos, currentBranch)
        return 2, currentBranch, None, None

           
    while j <= i:  # While not at end of suffix


        #jump to end of the branch if branch ends before the suffix
        if i - j + 1 > currentBranch.getEnd() - currentBranch.start + 1:

            #Remove remainder accordingly as a branch has been fully traversed
            remainder.decrease(currentBranch.getEnd() - currentBranch.start + 1)

            # check the next letter of the suffix for sub branch to go down
            j += currentBranch.getEnd() - currentBranch.start + 1 # jump to the emnd to compare sub-branches

            suffixLetter = s[j] #Letter one past end of branch, which you check for matching sub-branches
            suffixLetterNum =  ord(suffixLetter) #which element in array to take up
            
            if currentBranch.subNodes[suffixLetterNum] != None: # if there is a good sub-branch to go down follow it
                activeNode = currentBranch 
                currentBranch = currentBranch.subNodes[suffixLetterNum]

            else: # no good sub-branches to go down, make a new sub branch
                currentBranch.subNodes[suffixLetterNum] = Node(j, endPos, currentBranch)
                return 2, currentBranch, None, None # In this case current node has been fully traversed (so not activeNode returned)

        else: #suffix ends before/at-the-end-of the branch

            suffixLetter = s[i] # i is last letter of the suffix: [j....i] (and thus the letter to check)
            
            # if something ends 1 after the end of the branch
            if i - j + 1 == currentBranch.getEnd() - currentBranch.start + 1 + 1: # First +1 for length, second +1 for ending 1 after
                suffixLetterNum = ord(suffixLetter) #which element in array to take up

                if currentBranch.subNodes[suffixLetterNum] == None: # if a good sub-branch to go down follow it otherwise make one
                    currentBranch.subNodes[suffixLetterNum] = Node(j+1, endPos, currentBranch)

                else:
                    return 3, activeNode, None, i - j + 1

            #Suffix ends mid branch with mismatch
            elif suffixLetter != s[currentBranch.start + i - j + 1 - 1]:
                pendingNode = splitBranchInMiddle(s, currentBranch, j, endPos, i - j + 1 - 1) #i - j +1 is distance on the branch including last digit, so -1
                return 2, activeNode, pendingNode, None

            else: # Complete match, no action needed
                return 3, activeNode, None, i - j + 1
            
            raise ValueError("If statement escaped")

def fastSuffixTree(s):
    """Creates a suffix tree in O(n) using Ukkonen's"""

    #Change the last character of s from $ to \x00 so it works with new lines and other small ord characters
    if s[-1] != '$':
        raise ValueError(f"Expected s to end with unique character $ , found {s[-1]}")
    
    s = list(s[:-1]) + ['\x00'] #lowest possible unicode character

    # Initialise suffix tree
    root = Node(-1,-2, None, False)
    root.suffixLink = root

    #Set variables
    activeNode = root
    pending = Pending()
    remainder = Remainder()
    rem = None # Length of remainder found in last iteration
    lastJ = -1 #last rule 2 occurence
    globalEnd = BranchEndPos()
    rule = None


    # Iterate through the string
    for i in range(len(s)):
        
        #Increment the end pos 
        globalEnd.increment()

        for j in range(lastJ + 1, i + 1):

            rule, activeNode, newPend, rem = traverse(s,j,i,activeNode,remainder,globalEnd)
            pending.push(newPend)

            # Rule 2 with new internal node: pending goes to the node just created
            # Rule 3 or no internal node created: pending goes to the active node
            prevPend = pending.pull() # previouly pending, or None

            #resolve suffix links (only internal nodes can be pending)
            if prevPend:
                if newPend: # If new internal node created
                    prevPend.suffixLink = newPend 

                else: # No new internal node created
                    prevPend.suffixLink = activeNode

            #Follow suffix link if Rule 2 (not on Rule 3)
            if rule == 2:

                #If going from root to root reduce remainder by one
                if activeNode == root:
                    remainder.decrease(1)

                activeNode = activeNode.suffixLink #Every active node should have a suffix link
                lastJ = j

            # Incresse remainder if Rule 3
            elif rule == 3:
                remainder.increase(i - rem + 1,i)
                break #End iteration since everything else will rule 3

            else:

                raise ValueError(f"Rule = {rule}")
            
    return root

     
while True:
    s = input("String to find suffix array of: ")
    print(suffixTreeDFS(fastSuffixTree(s), len(s)))
    