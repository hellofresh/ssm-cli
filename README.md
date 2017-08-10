# ssm-cli
CLI for setting and retrieving parameters and secrets from AWS SSM.


## Installation

TODO

## Usage
Running:
```
./ssm.py
```

### List parameters

List all parameters:
```
./ssm.py list
```

Filter parameters by name:
```
./ssm.py list hello world
```
Will list parameters starting with `hello` and `world`


### File

The file options takes a python config file as an input and performs actions based on the sections in the file.

For example a file containing:

```
[list]
hello
world
```

Will list parameters starting with `hello` and `world` as follows:
```
[list]
hello
hello1
world
world2
```
