import boto3
import ssm
import tempfile

from moto import mock_ssm


@mock_ssm
def test_list_no_arg():
    conn = boto3.client('ssm')
    # Create two parameters and check both are returned
    conn.put_parameter(Name='test', Value='testing123', Type='SecureString')
    conn.put_parameter(Name='test1', Value='testing123', Type='SecureString')

    # Call list without any parameters
    out = ssm.list_param(conn)

    assert len(out) == 2
    assert 'test1' in out
    assert 'test' in out


@mock_ssm
def test_list_starts_with():
    conn = boto3.client('ssm')
    # Create two parameters and check both are returned
    conn.put_parameter(Name='test1', Value='testing123', Type='SecureString')
    conn.put_parameter(Name='anotherValue', Value='testing123', Type='SecureString')

    out = ssm.list_param(conn, ["test"])

    assert len(out) == 1
    assert 'test1' in out
    assert 'anotherValue' not in out


@mock_ssm
def test_file_list():
    # Create a temp file
    test_file = tempfile.NamedTemporaryFile(delete=False)

    conn = boto3.client('ssm')
    conn.put_parameter(Name='test1', Value='ali', Type='SecureString')
    conn.put_parameter(Name='test2', Value='ali', Type='SecureString')
    conn.put_parameter(Name='anotherValue', Value='ali', Type='SecureString')

    test_file.write('''[list]
test''')
    test_file.close()

    result = ssm.process_file(conn, test_file.name)

    assert 'list' in result.keys()
    assert 'test1' in result['list']
    assert 'test2' in result['list']
    assert 'anotherValue' not in result['list']
