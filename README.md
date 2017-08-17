# ssm-cli
CLI for setting and retrieving parameters and secrets from AWS SSM.


## Installation
From the root project directory:
```
pip install .
```

## Usage
Running:
```
ssm --help
```

### List parameters

List all parameters:
```
ssm list
```
Output:
```
+------------------------------------+---------------+
| Name                               | Description   |
+====================================+===============+
| /platform/infra/testing            | Test param    |
+------------------------------------+---------------+
| MY_KEY                             | MY TEST KEY   |
+------------------------------------+---------------+
```
Filter parameters by name:
```
ssm list --name hello
```
Will list parameters starting with `hello`
```
+--------+---------------+
| Name   | Description   |
+========+===============+
| hello1 | world1        |
+--------+---------------+
```

### Delete Parameters
```
ssm delete --name myparam --delete invalid
```
Will delete the parameter `myparam`, invalid parameters are ignored and printed on stdout.
Output:
```
+----------------------+
| Deleted Parameters   |
+======================+
| myparm               |
+----------------------+
+----------------------+
| Invalid Parameters   |
+======================+
| invalid              |
+----------------------+
```
### Get parameters
```
ssm get --name MY_KEY
```
Will retrieve and decrypt the param MY_KEY
Output:
```
+--------+---------+
| Name   | Value   |
+========+=========+
| MY_KEY | MY_VAL  |
+--------+---------+
```

### Put parameters
```
ssm put --name <name> --value <value> --description <optional description> --encrypt
```
