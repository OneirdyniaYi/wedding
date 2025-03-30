import re
import json
import logging



class CustomFunction:
    def __init__(self, story_json_data,bug_json_data):
        self.story_data_table = json.loads(story_json_data)
        self.bug_data_table = json.loads(bug_json_data)
        
    
    def tokenize(self,formula):
        pattern = r'\{.*?\}|[+/*()-]'
        tokens = re.findall(pattern, formula)
        logging.getLogger('DEBUG').info(f"CustomFunction tokens:{tokens}")
        return tokens

    def shunting_yard(self,tokens):
        precedence = {'+': 2, '-': 2, '*': 3, '/': 3, '(': 1}
        output = []
        stack = []
        for token in tokens:
            if token in precedence:
                while stack and stack[-1] != '(' and precedence[token] <= precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append(token)
            elif token == ')':
                while stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            else:
                output.append(token)
        while stack:
            output.append(stack.pop())
        return output

    def algorithm(self,item:str):
        sum = 0
        itemDict = json.loads(item)
        res = {}
        if itemDict['type'] == 'story':
            for id,data in self.story_data_table.items():
                for key,value in data.items():
                    if key == itemDict['name']:
                        if '__all__' in itemDict and itemDict['__all__'] == 1:
                            if '__all__' not in res:
                                res['__all__'] = 0
                            sum += 1
                            res['__all__'] += 1
                        elif 'evals' in itemDict and value in itemDict['evals']:
                            if value not in res:
                                res[value] = 0
                            res[value] += 1
                            sum += 1
                        elif 'noevals' in itemDict and value not in itemDict['noevals']:
                            if value not in res:
                                res[value] = 0
                            res[value] += 1
                            sum += 1
                        elif 'range' in itemDict and value >= itemDict['range'][0] and value <= itemDict['range'][1]:
                            if value not in res:
                                res[value] = 0
                            res[value] += 1
                            sum += 1
        elif itemDict['type'] == 'bug':
            for id,data in self.bug_data_table.items():
                for key,value in data.items():
                    if key == itemDict['name']:
                        if '__all__' in itemDict and itemDict['__all__'] == 1:
                            if '__all__' not in res:
                                res['__all__'] = 0
                            sum += 1
                            res['__all__'] += 1
                        elif 'evals' in itemDict and value in itemDict['evals']:
                            if value not in res:
                                res[value] = 0
                            res[value] += 1
                            sum += 1
                        elif 'noevals' in itemDict and value not in itemDict['noevals']:
                            if value not in res:
                                res[value] = 0
                            res[value] += 1
                            sum += 1
                        elif 'range' in itemDict and value >= itemDict['range'][0] and value <= itemDict['range'][1]:
                            if value not in res:
                                res[value] = 0
                            res[value] += 1
                            sum += 1
        return sum,{"name":itemDict['name'],"type":itemDict['type'],"values":res}
    

    def evaluate(self,postfix):
        stack = []
        res = []
        for token in postfix:
            if token in '+-*/':
                b = stack.pop()
                a = stack.pop()
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    if b == 0:
                        stack.append(0)
                    else:
                        stack.append(a / b)
            else:
                count,itemRes = self.algorithm(token)
                res.append(itemRes)
                logging.getLogger('DEBUG').info(f"CustomFunction token is {token} ,count is {count}")
                stack.append(count)
        return stack[0],res
    
    def calculate(self,formula):
        tokens = self.tokenize(formula)
        postfix = self.shunting_yard(tokens)
        result,itemsCount = self.evaluate(postfix)
        return result,itemsCount