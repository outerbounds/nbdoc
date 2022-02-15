
from metaflow import FlowSpec, step

class MyFlow(FlowSpec):
    
    @step
    def start(self):
        print('this is the start')
        self.next(self.end)
    
    @step
    def end(self):
        print('this is the end')

if __name__ == '__main__':
    MyFlow()
