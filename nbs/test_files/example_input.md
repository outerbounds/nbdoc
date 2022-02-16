---
title: my hello page title
description: my hello page description
hide_table_of_contents: true
---
## This is a test notebook

This is a shell command:


```bash
echo hello
```

    hello


We are writing a python script to disk:


```py title="myflow.py"
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
```

Another shell command where we run a flow:


```bash
python myflow.py run
```

    2022-02-15 14:11:09.224 [1644963069213536/start/1 (pid 46840)] Task is starting.
    2022-02-15 14:11:09.858 [1644963069213536/start/1 (pid 46840)] this is the start
    2022-02-15 14:11:09.929 [1644963069213536/start/1 (pid 46840)] Task finished successfully.
    ...

This is a normal python cell:




    2



The next cell has a cell tag of `remove_input`, so you should only see the output of the cell:

    hello, you should not see the print statement that produced me

