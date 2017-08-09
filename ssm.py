#!/usr/bin/python

import argparse
import boto3
import ConfigParser
import logging


def list_param(client, values=[]):
    """List implementation."""
    if values:
        filters = [{"Key": "Name", "Values": values}]
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


def process_file(client, in_file):
    config = ConfigParser.SafeConfigParser(allow_no_value=True)
    read_file_list = config.read(in_file)
    result = {}

    if not read_file_list:
        logger.error("Couldn't read file.")

    if config.has_section('list'):
        out = list_param(client, [item[0] for item in config.items('list')])
        if out:
            result['list'] = out
    else:
        logger.error("No valid section found in the provided file.")
    return result


def main():
    """Main function."""
    args = parser.parse_args()
    # Create the boto client
    ssm_client = boto3.client('ssm')

    if args.command == 'list':
        results = list_param(ssm_client, args.values, args.exact)
        for param in results:
            logger.info(param)
    elif args.command == "file":
        results = process_file(ssm_client, args.location)
        for k in results.keys():
            if results[k]:
                logger.info("[%s]" % k)
                for value in results[k]:
                    logger.info(value)
    if not results:
        # Exit with error if nothing found
        exit(1)

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

if __name__ == '__main__':
    main()
