import boto3
import click
import yaml
from tabulate import tabulate


@click.group()
@click.version_option()
def cli():
    """CLI for retrieving and setting parameters and secrets using AWS SSM."""


def list_params(names):
    client = boto3.client('ssm')
    if names:
        filters = [{"Key": "Name", "Values": names}]
    # The whole list needs to be empty
    else:
        filters = []
    try:
        paginator = client.get_paginator('describe_parameters')
        response_iterator = paginator.paginate(Filters=filters)
    # TODO: catch  exceptions
    except Exception as e:
        click.echo("Error listing parameters:")
        click.echo(e.message)
        exit(1)

    output = []
    for page in response_iterator:
        for param in page['Parameters']:
            if 'Description' not in param:
                param['Description'] = ''
            output.append(dict(Name=param.get('Name'), Description=param.get('Description')))
    return output


@cli.command()
@click.option('--name', '-n', metavar='<name>', multiple=True, help='Show parameters starting with <name>')
def list(name):
    """List available parameters."""
    output = list_params(name)
    if output:
        click.echo(tabulate({'Name': [item['Name'] for item in output],
                             'Description': [item['Description'] for item in output]},
                            headers='keys', tablefmt='grid'))
    else:
        click.echo("No parameters found.")


def delete_params(names):
    client = boto3.client('ssm')
    try:
        response = client.delete_parameters(Names=names)
    # TODO: catch  exceptions
    except Exception as e:
        click.echo("Error deleting parameters:")
        click.echo(e.message)
        exit(1)
    return response.get('DeletedParameters'), response.get('InvalidParameters')


@cli.command()
@click.option('--name', '-n', metavar='<name>', multiple=True, required=True, help='Name of the parameter to delete')
def delete(name):
    """Delete parameters with <name>."""
    output, err = delete_params(name)
    # Print if specified otherwise return output
    if output:
        click.echo(tabulate({'Deleted Parameters': output}, headers='keys', tablefmt='grid'))
    if err:
        click.echo(tabulate({'Invalid Parameters': err}, headers='keys', tablefmt='grid'))


def get_params(names):
    client = boto3.client('ssm')
    try:
        response = client.get_parameters(Names=names, WithDecryption=True)
    # TODO: catch  exceptions
    except Exception as e:
        click.echo("Error getting parameters")
        click.echo(e.message)
        exit(1)
    return response.get('Parameters'), response.get('InvalidParameters')


@cli.command()
@click.option('--name', '-n', metavar='<name>', multiple=True, required=True, help='Name of the parameter to retrieve')
def get(name, print_output=True):
    """Retrieve values of parameters with <name>."""
    output, err = get_params(name)
    if output:
        click.echo(tabulate({'Name': [param['Name'] for param in output],
                             'Value': [param['Value']for param in output]},
                            headers='keys', tablefmt='grid'))
    if err:
        click.echo(tabulate({'Invalid Parameters': [param for param in err]},
                            headers='keys', tablefmt='grid'))


def put_param(name, value, encrypt, description=None):
    client = boto3.client('ssm')

    if encrypt:
        param_type = 'SecureString'
    else:
        param_type = 'String'
    try:
        if description:
            client.put_parameter(Name=name, Value=value, Description=description,
                                 Overwrite=True, Type=param_type)
        else:
            client.put_parameter(Name=name, Value=value, Overwrite=True, Type=param_type)
    except Exception as e:
        click.echo("Error putting parameters")
        click.echo(e.message)
        exit(1)
    # return the name of the variable in case of success
    return name


@cli.command()
@click.option('--name', '-n', metavar='<name>', required=True, help='Name of the parameter')
@click.option('--value', '-v', metavar='<value>', required=True, help='Value of the parameter')
@click.option('--description', '-d', metavar='<description>', help='Description for the parameter')
@click.option('--encrypt', '-e', is_flag=True, default=False, help='Encrypt the parameter')
def put(name, value, description, encrypt):
    """Put parameter with name <name>, value <value> and description <description>. Optionally encrypt the parameter."""
    output = put_param(name=name, value=value, description=description, encrypt=encrypt)
    if output:
        click.echo(tabulate({'Created Parameters': [output]}, headers='keys', tablefmt='grid'))


@cli.command(name="from-file")
@click.option('--path', '-p', metavar='<path>', required=True, type=click.File('r'), help='Path to the file')
def from_file(path):
    """Parse commands from the given <path>"""
    # TODO: Exceptions
    data = yaml.load(path)
    output = {}

    if not set(data.keys()).issubset(set(['list', 'get', 'delete', 'put'])):
        click.echo("Invalid keys in file, supported keys are: list, get, delete and put.")
        exit(1)
    for key, value in data.items():
        if key == 'list':
            output['list'] = list_params(value)
        elif key == 'get':
            output['get'] = {}
            out, err = get_params(value)
            if out:
                output['get']['GetParameters'] = out
            if err:
                output['get']['InvalidParameters'] = err
        elif key == 'delete':
            out, err = delete_params(value)
            output['delete'] = {}
            if out:
                output['delete']['DeletedParameters'] = out
            if err:
                output['delete']['InvalidParameters'] = err
        elif key == 'put':
            output['put'] = {'CreatedParameters': []}
            for param in value:
                output['put']['CreatedParameters'].append(put_param(**param))

    click.echo(yaml.safe_dump(output, default_flow_style=False))
