SA.py
===

* Usage: python SA.py < ${testcase} > ${output}

## Verifier
* Usage (temporarily)
  1. python3 verifier.py < ${testcase_input}
  2. Set OUT_FILE in verifier.py to ${testcase_output}.

## Testcase Generator
It generates testcases. Then it creates a directory, and put those testcases in the directory.

### How to run
```shell
$ python3 testcase_generator_v2.py
```

### Config
You can see [here](https://docs.google.com/presentation/d/1waslqtZd9denwGSDetzCeeoGvWF2v87SsqomDUJ0CRk/edit?usp=sharing) to know more.
```python
config = {
    # This will be the name of the directory.
    'TESTCASE_NAME': 'workload',

    # Number of testcases you want to generate.
    'TESTCASE_NUMS': 5,

# ------------- Testcase Settings -------------------------
    # The servers will be allocated at a X * Y grid.
    # J should always eqaul to X * Y.
    'X': 2,
    'Y': 3,
    'J': 6,

    # The number of vehicles.
    'I': 10,
    
    # The number of service types.
    'K': 5,
    # The time unit limit
    'MAX_TIME': 100,
    'EARLIEST_DEADLINE': 80,

    # The properties of a service.
    'DIFF_LOW': 1,
    'DIFF_HIGH': 3,
    'ABILITY_LEVEL': 2,
    'PROB_LOW': 0.2,
    'PROB_HIGH': 0.8,

    'FRESHNESS_MEAN': 50,
    'FRESHNESS_STD': 30,

    'LINGER_MEAN': 15,
    'LINGER_STD': 10,

    'MEMORY_MEAN': 20,
    'MEMORY_STD': 5
}
```

### Workload Estimation
The filenames of a generated testcase will be in terms of `{testcase_index}_{estimated_workload}.in`. For example, `1_0.067.in`.

The workload is estmated by the formulation below, where $E[C_k]$ is the expected computed time of a service.
$$W = \frac{I \times \sum_k{E[C_k]}}{J \times T}$$

### 2021/04/12 New Testcase Format
Update R format to reduce file size.
```python
# example
# There are I rows, each row specifies the route of vehicle i.
# Every row is several pairs of number separated by ",".
# For example:
# 22 1, 10 3, 12 2, 8 4, 5 2, 20 0, 6 2, 17 4
# The sequence above tells the route where the vehicle is in
# server 1 when t = 0, 1, 2, ..., 21
# server 3 when t = 22, 23, 24, ..., 31
# ...
# server 4 when t = ...., MAX_TIME-1
```
