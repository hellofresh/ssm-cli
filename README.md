<p align="center">
  <a href="https://hellofresh.com">
    <img width="120" src="https://www.hellofresh.de/images/hellofresh/press/HelloFresh_Logo.png">
  </a>
</p>

[![Build Status](https://travis-ci.org/hellofresh/ssm-cli.svg?branch=master)](https://travis-ci.org/hellofresh/ssm-cli)

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
## Configuring Credentials
The Following authentication methods are supported:
* Environment variables
* Shared credential file (~/.aws/credentials)
* AWS config file (~/.aws/config)

For more details please see [here](http://boto3.readthedocs.io/en/latest/guide/configuration.html).

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


### From file
Multiple operation can be done using the `from-file` option.
#### Usage
Specify the path to a yaml file using the `--path <path>` option:
```
ssm from-file --path <path to yaml file>
```
#### Format
The file should be a valid yaml file with the keys equal to the operations namely:

* list
* get
* delete
* put

Multiple operation can be specified in one file.


#### Examples

##### put
```
put:
    - name: test
      value: val
      encrypt: True
```
Output:
```
put:
  CreatedParameters:
  - test
```

##### list
```
list:
    - someparam
    - anotherparam
```
Output:
```
list:
- Description: Some Parameter
  Name: someparam
- Description: Another Parameter
  Name: anotherparam

```
#### delete
```
delete:
  - validparam
  - invalidparam
```
Output:
```
delete:
  DeletedParameters:
  - x14
  InvalidParameters:
  - invalidparam
````
#### get
```
get:
  - test
  - invalid
```
Output:
```
get:
  GetParameters:
  - Name: test
    Type: SecureString
    Value: val
  InvalidParameters:
  - invalid
```
