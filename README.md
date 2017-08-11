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

### Delete Parameters
```
./ssm.py delete "myparam" "invalid"
```
Output:
```
DeletedParameters:
myparam
InvalidParameters:
invalid
```
Will delete the parameter `myparam`, invalid parameters are ignored and printed on stdout.

### File

The file options takes a python config file as an input and performs actions based on the sections in the file.

#### List
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
#### Delete
```
[delete]
hello1
Invalid
```
Will try to delete the listed parameters as follows:
```
[delete.DeletedParameters]
hello1
[delete.InvalidParameters]
Invalid
```
Deleted parameters are listed in the `delete.DeletedParameters` section while invalid parameters are listed in the `delete.InvalidParameters`.
