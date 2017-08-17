import boto3
import click
from tabulate import tabulate


@click.group()
@click.version_option()
def cli():
    """CLI for retrieving and setting parameters and secrets using AWS SSM."""


@cli.command()
@click.option('--name', '-n', metavar='<name>', multiple=True, help='Show parameters starting with <name>')
def list(name, print_output=True):
    """List available parameters."""
    client = boto3.client('ssm')
    if name:
        filters = [{"Key": "Name", "Values": name}]
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
    # Print if specified otherwise return output
    if print_output:
        if output:
            click.echo(tabulate({'Name': [item['Name'] for item in output],
                                 'Description': [item['Description'] for item in output]},
                                headers='keys', tablefmt='grid'))
        else:
            click.echo("No parameters found.")

    return output


@cli.command()
@click.option('--name', '-n', metavar='<name>', multiple=True, required=True, help='Name of the parameter to delete')
def delete(name, print_output=True):
    """Delete parameters with <name>."""
    # Return empty if nothing is provided
    client = boto3.client('ssm')
    try:
        response = client.delete_parameters(Names=name)
    # TODO: catch  exceptions
    except Exception as e:
        click.echo("Error deleting parameters:")
        click.echo(e.message)
        exit(1)
    # Print if specified otherwise return output
    if print_output:
        if response.get('DeletedParameters'):
            click.echo(tabulate({'Deleted Parameters': response['DeletedParameters']}, headers='keys', tablefmt='grid'))
        if response.get('InvalidParameters'):
            click.echo(tabulate({'Invalid Parameters': response['InvalidParameters']}, headers='keys', tablefmt='grid'))

    return response.get('DeletedParameters'), response.get('InvalidParameters')


@cli.command()
@click.option('--name', '-n', metavar='<name>', multiple=True, required=True, help='Name of the parameter to retrieve')
def get(name, print_output=True):
    """Retrieve values of parameters with <name>."""
    client = boto3.client('ssm')
    try:
        response = client.get_parameters(Names=name, WithDecryption=True)
    # TODO: catch  exceptions
    except Exception as e:
        click.echo("Error getting parameters")
        click.echo(e.message)
        exit(1)

    if print_output:
        if response.get('Parameters'):
            click.echo(tabulate({'Name': [param['Name'] for param in response['Parameters']],
                                 'Value': [param['Value']for param in response['Parameters']]},
                                headers='keys', tablefmt='grid'))
        if response.get('InvalidParameters'):
            click.echo(tabulate({'Invalid Parameters': [param for param in response['InvalidParameters']]},
                                headers='keys', tablefmt='grid'))

    return response.get('Parameters'), response.get('InvalidParameters')


@cli.command()
@click.option('--name', '-n', metavar='<name>', required=True, help='Name of the parameter')
@click.option('--value', '-v', metavar='<value>', required=True, help='Value of the parameter')
@click.option('--description', '-d', metavar='<description>', help='Description for the parameter')
@click.option('--encrypt', '-e', is_flag=True, default=False, help='Encrypt the parameter')
def put(name, value, description, encrypt):
    """Put parameter with name <name>, value <value> and description <description>. Optionally encrypt the parameter."""
    client = boto3.client('ssm')

    if encrypt:
        param_type = 'SecureString'
    else:
        param_type = 'String'
    try:
        client.put_parameter(Name=name, Value=value, Description=description,
                             Overwrite=True, Type=param_type)
    except Exception as e:
        click.echo("Error putting parameters")
        click.echo(e.message)
        exit(1)
    # return the name of the variable in case of success
    return name
