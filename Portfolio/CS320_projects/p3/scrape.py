# project: p3
# submitter: apierrelouis
# partner: none
# hours: 10
import copy
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import pandas as pd
import time
import requests

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set and order list
        self.visited.clear()
        self.order.clear()
        # 2. start recursive search by calling dfs_visit
        self.dfs_visit(node)

    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        if node in self.visited:
            return
        # 2. mark node as visited by adding it to the set
        self.visited.add(node)
        # 3. call self.visit_and_get_children(node) to get the children
        children = self.visit_and_get_children(node)
        # 4. in a loop, call dfs_visit on each of the children
        for child in children:
            self.dfs_visit(child)
    
    def bfs_search(self, node):
        self.visited.clear()
        self.order.clear()
        self.bfs_visit(node)
        
    def bfs_visit(self, node):
        self.visited.add(node)
        to_visit = self.visit_and_get_children(node)
        
        while len(to_visit) > 0:
            curr = to_visit.pop(0)
            if curr in self.visited:
                continue
            self.visited.add(curr)
            children = self.visit_and_get_children(curr)
            for child in children:
                if child not in to_visit:
                    to_visit.append(child)
            
    
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df

    def visit_and_get_children(self, node):
        # TODO: Record the node value in self.order
        self.order.append(node)
        children = []
        # TODO: use `self.df` to determine what children the node has and append them
        for child, has_edge in self.df.loc[node].items():
            if has_edge==1:
                children.append(child)
        return children
    

class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        
    def visit_and_get_children(self, file):
        node = None
        with open("./file_nodes/"+file, 'r') as f:
            node = str(f.readline()).strip()
            self.order.append(node)
            children = str(f.readline()).strip().split(',')
        return children
    
    def concat_order(self):
        order = copy.copy(self.order)
        retstr = ""
        for val in order:
            retstr += val
        return retstr
    
    
class WebSearcher(GraphSearcher):
    def __init__(self,driver):
        super().__init__()
        self.driver = driver
        
    def visit_and_get_children(self, url):        
        self.order.append(url)
        
        self.driver.get(url)
        children = []
        alist = self.driver.find_elements("tag name", "a")
        for a in alist:
            #print(a.get_attribute('href'))
            children.append(a.get_attribute('href'))
        #self.driver.close()
        return children
    
    def table(self):        
        df = pd.DataFrame()
        for url in self.order:
            dfnext = pd.read_html(url)
            #print(dfnext)
            df=pd.concat([df, dfnext[0]], ignore_index=True)
        return df#.to_string()
    

def reveal_secrets(driver, url, travellog):
    cluelist = travellog['clue'].tolist()
    pswrd = ''.join(str(clue) for clue in cluelist)
    
    driver.get(url)
    div = driver.find_element("tag name", "div")
    h3list = div.find_elements("tag name", "h3")
    passbox = h3list[2].find_element("id", "password-textbox")
    passbutton = h3list[2].find_element("id", "submit-button")
    
    passbox.send_keys(pswrd)
    time.sleep(0.1)
    passbutton.click()
    time.sleep(0.1)
    
    driver.find_element("id", "view-location-button").click()
    time.sleep(1)
    
    div2 = driver.find_elements("tag name", "div")[1]
    img_el = div2.find_element("tag name", "img")
    img_link = img_el.get_attribute('src')
    #filename = img_link.split('/')[-1]
    
    req = requests.get(img_link, stream=True)
    with open('Current_Location.jpg', 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024): #I don't know whether to use 1024 default chunk size or 500 since thats the width of the image pixels but it works so
            if chunk: # code for if statement and for loop inspired from forum: https://stackoverflow.com/questions/53101597/how-to-download-binary-file-using-requests
                f.write(chunk)
    
    text = div2.find_element("tag name", "p").text
    
    return text.strip()