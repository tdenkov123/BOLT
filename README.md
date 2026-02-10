# BOLT (Block-Oriented Lightweight Tasker)

This is a lightweight runtime system supposed to run Function Blocks (FBs).

# How to start

Create venv, activate it and install deps
```bash
$ python -m venv .venv
$ source ./.venv/bin/activate
$ pip install -r requirements.txt 
```
Then start
```bash
$ python main.py
```

Bonus: this code uses threads on every event chain, so if you want to boost up performance of BOLT, it is recommended to turn the GIL off.