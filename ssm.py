#!/usr/bin/python

import argparse
import boto3
import ConfigParser
import logging


def list_param(client, params=[]):
    """List implementation."""
    if params:
        filters = [{"Key": "Name", "Values": params}]
    # The whole list needs to be empty
    else:
        filters = []
    try:
        paginator = client.get_paginator('describe_parameters')
        response_iterator = paginator.paginate(Filters=filters)
    # TODO: catch  exceptions
    except Exception as e:
        logger.error("Error listing parameters:")
        logger.error(e.message)
        exit(1)

    output = []
    for page in response_iterator:
        for param in page['Parameters']:
            output.append(param['Name'])
    return output


def delete_param(client, params):
    """Delete parameters."""
    # Return empty if nothing is provided
    try:
        response = client.delete_parameters(Names=params)
    # TODO: catch  exceptions
    except Exception as e:
        logger.error("Error deleting parameters:")
        logger.error(e.message)
        exit(1)
    return response['DeletedParameters'], response['InvalidParameters']


def process_file(client, in_file):
    """Parse file for commands and execute."""
    config = ConfigParser.SafeConfigParser(allow_no_value=True)
    read_file_list = config.read(in_file)
    result = {'list': [], 'delete': {"DeletedParameters": [],
                                     "InvalidParameters": []
                                     }}

    if not read_file_list:
        logger.error("Couldn't read file.")
    sections = config.sections()

    for section in sections:
        if section == 'list':
            out = list_param(client, [item[0] for item in config.items('list')])
            if out:
                result['list'].extend(out)
        elif section == 'delete':
            out, err = delete_param(client, [item[0] for item in config.items('delete')])
            if out:
                result['delete']['DeletedParameters'].extend(out)
            if err:
                result['delete']['InvalidParameters'].extend(err)
    return result


def print_dict(in_dict, parent=''):
    """Print a given dict nicely."""
    for k, v in in_dict.iteritems():
        if isinstance(v, dict):
            print_dict(v, k)
        elif v:
            if parent:
                logger.info("[%s.%s]" % (parent, k))
            else:
                logger.info("[%s]" % k)
            for item in v:
                logger.info(item)


def main():
    """Main function."""
    args = parser.parse_args()
    # Create the boto client
    ssm_client = boto3.client('ssm')

    if args.command == 'list':
        results = list_param(ssm_client, args.values)
        for param in results:
            logger.info(param)
    elif args.command == 'delete':
        results, failed = delete_param(ssm_client, args.values)
        if results:
            logger.info("DeletedParameters:")
            for param in results:
                logger.info(param)
        if failed:
            logger.info("InvalidParameters:")
            for param in failed:
                logger.info(param)
    elif args.command == "file":
        results = process_file(ssm_client, args.location)
        print_dict(results)

# Create logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


parser = argparse.ArgumentParser(description='Get / Set secrets')

subparsers = parser.add_subparsers(title='subcommands', dest='command',
                                   description='valid subcommands')
# file
subparser_file = subparsers.add_parser('file', help='Use a config file for actions')
subparser_file.add_argument('location', help='Path to the file')
# List
subparser_list = subparsers.add_parser('list', help='List parameters')
subparser_list.add_argument('values', type=str, nargs='*', help= 'Display parameters starting with provided arugments')
# Delete
subparser_delete = subparsers.add_parser('delete', help='Delete parameters')
subparser_delete.add_argument('values', type=str, nargs='+', help= 'Delete the given parameters')

if __name__ == '__main__':
    main()
