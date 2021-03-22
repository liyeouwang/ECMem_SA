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

    'LINEGER_MEAN': 15,
    'LINGER_STD': 10,

    'MEMORY_MEAN': 20,
    'MEMORY_STD': 5
}
```