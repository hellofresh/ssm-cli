import boto3
import ssm
from click.testing import CliRunner

from moto import mock_ssm


@mock_ssm
def test_list_no_arg():
    conn = boto3.client('ssm')
    # Create two parameters and check both are returned
    conn.put_parameter(Name='test1', Value='testing1', Type='SecureString')
    conn.put_parameter(Name='test2', Value='testing2', Type='SecureString')

    # Call list without any parameters
    runner = CliRunner()
    result = runner.invoke(ssm.list)

    assert "No parameters found" not in result.output
    assert 'test1' in result.output
    assert 'test2' in result.output


@mock_ssm
def test_list_starts_with():
    conn = boto3.client('ssm')
    # Create two parameters and check both are returned
    conn.put_parameter(Name='test1', Value='testing123', Type='SecureString')
    conn.put_parameter(Name='anotherValue', Value='testing123', Type='SecureString')

    runner = CliRunner()
    result = runner.invoke(ssm.list, ['--name', 'test'])

    assert 'test1' in result.output
    assert 'anotherValue' not in result.output


@mock_ssm
def test_get_param():
    conn = boto3.client('ssm')

    # Create two parameters and check both are returned
    conn.put_parameter(Name='test1', Value='value1', Type='SecureString')
    conn.put_parameter(Name='test2', Value='value2', Type='SecureString')

    runner = CliRunner()
    result = runner.invoke(ssm.get, ['--name', 'test1'])

    assert 'Invalid Parameters' not in result.output
    assert 'value1' in result.output
    assert 'test1' in result.output

    assert 'test2' not in result.output
    assert 'value2' not in result.output


@mock_ssm
def test_delete_correct():
    conn = boto3.client('ssm')
    # Create a parameter and check if it is deleted.
    conn.put_parameter(Name='test1', Value='testing123', Type='SecureString')

    runner = CliRunner()
    result = runner.invoke(ssm.delete, ['--name', 'test1'])
    assert 'Deleted Parameters' in result.output
    assert 'test1' in result.output
    # Check if parameter is actually deleted
    runner = CliRunner()
    result = runner.invoke(ssm.list, ['--name', 'test1'])
    assert 'No parameters found' in result.output


@mock_ssm
def test_delete_invalid():
    conn = boto3.client('ssm')

    # Delete an invalid parameter
    runner = CliRunner()
    result = runner.invoke(ssm.delete, ['--name', 'invalid_param'])

    assert 'Invalid Parameters' in result.output
    assert 'invalid_param' in result.output
    assert 'Deleted Parameters' not in result.output
