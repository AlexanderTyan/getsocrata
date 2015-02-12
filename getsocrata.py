"""

Run with the -h argument for help.

This module may be run from the command line or may be imported into a larger project.

The module uses Socrata Open Data Api (SODA) Version 1
This uses the deprecated authentication format with no callback URL. Socrata may 
discontinue this request type in the future in favor of a callback URL method.


Review Notes 021115:
    1. App should allow unauthenticated requests.
    2. App should gracefully handle failed requests (It may already).
    3. It would be good to move to the current SODA API version 2 (we are on V1 oauth).
    4. App should support Python 3 too.

"""

import json
import requests
import argparse
import ConfigParser
import sys
import os
import datetime
import urllib
import traceback

import pickle

http_request_history = {}
getsocrata_options = {}

gl_total_list = []


def get_socrata_data(token, source_url, output_file):
    """ Retrieve and turn a list of json objects (records) from a socrata API endpoint.

    This specific setup has been tested on SFgov's Socrata API.

    This uses the deprecated authentication format with no callback URL. Socrata may 
    discontinue this request type in the future in favor of a callback URL method.
    """

    socrata_headers = { 'X-App-Token' : token }
    
    tries = 3 # try at least 3 times 
    r = None  # Need r in this scope for while/else statement
    while tries > 0:
        try:
            r = requests.get(url=source_url, headers=socrata_headers)
        except Exception as e:
            tries -= 1
            print "Request error:", sys.exc_info()[0], "trying", tries, "more times."
            continue

        http_request_history[source_url] = r.status_code
        if str(r.status_code) == '200':
            # Write successful attempt to log.
            with open(output_file+".log", "a+") as f:
                f.write(json.dumps({'time of request': datetime.datetime.now().strftime("%m.%d.%Y,%H:%M:%S"), str(source_url) : str(r.status_code)}) + os.linesep)
            return r.json()
        else:
            tries -= 1
            print "HTTP Request Failed! Retrying", tries, "more times..."
            continue
    # In the event that we have a failure, record it into a log file so it can be tracked and continue on.
    else:
        # Some errors do not ever assign a status code, so we'll assign one if r remains 'None'
        if r == None:
            status_code = 0
        else:
            status_code = r.status_code

        print "Failed:", str(source_url), "Response:", str(status_code)
        with open(output_file+".log", "a+") as f:
            f.write(json.dumps({'time of request': datetime.datetime.now().strftime("%m.%d.%Y,%H:%M:%S"), str(source_url) : str(status_code)}) + os.linesep)

        # if we returned [] then we couldn't tell the difference between a failed response and the end of the data stream.
        return None 


def parse_config_file(config_filename):
    """ Load a configuration file into the configuration dict and return it.

    This is really just a controller function for using the generic retrieve_config() function.
    """

    # placeholder - we need to check to make sure the file actually exists before trying to use it!

    getsocrata_options = {}

    getsocrata_options = retrieve_config(config_filename, 'getsocrata')
    getsocrata_options['filters'] = retrieve_config(config_filename, 'getsocrata filters')

    return getsocrata_options


def retrieve_config(config_filename="simple.config", section="getsocrata"):
    """Read and return configuration values from a configuration file.
    
    This is a generic function for moving key-value pairs from a ConfigParser config file into a dictionary.
    """
    config = ConfigParser.SafeConfigParser()
    try:
        config.read(config_filename)
    except: # Catch any unexpected configuration file issues and raise.
        print "Unexpected Error: Configuration file error. Check name and format.", sys.exc_info()
        raise

    config_dict = {}

    # Iterate over a list of all the options provided in a section.
    try:
        for arg_key in config.options(section):
            config_dict[arg_key] = config.get(section, arg_key)
    except ConfigParser.NoSectionError:
        print "Warning: No config section '" + str(section) + "' Returning an empty dictionary for this section."
        return {}

    return config_dict


def generate_filename(filename_base='myproject'):
    """ Use a timestamp and an optional project name to make a unique filename.

    """

    return filename_base + "." + datetime.datetime.now().strftime("%m%d%Y.%H%M%S") + ".json"


class MissingArgumentException(Exception):
    """ Exception class for when a critical argument is not passed before it is needed. 

    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def build_url_and_query_string(getsocrata_options):
    """Builds url string from user provided socrata SODA api parameters.

    Question: Can URL QueryStrings be ordered? Does the order matter? Does socrata need the order or respect the order?
    """

    generated_url = ""
    accepted_querystrings = ["$select", "$where", "$order", "$group", "$limit", "$offset"]
    
    #append base URL and begin querystring
    generated_url += getsocrata_options['url'] + "?"

    #socrata filters - use urllib's urlencode to ensure spaces and other special characters are encoded.
    generated_url += urllib.urlencode(getsocrata_options['filters']).replace('+','%20')

    #socrata SoQL queries
    for key, value in getsocrata_options.iteritems():
        if key in accepted_querystrings:
            #generated_url += "&"+str(key)+"="+str(value)
            generated_url += "&"+urllib.urlencode([(key, value)]).replace('+','%20')

    return generated_url


def increment_offset_and_record_data_until_empty(control_iterative_function, control_ending_function):
    """ This control loop iteratively pulls data until it runs out
    
    """

    next_page = None   # Utilized in the while loop below
    while next_page != []:

        next_url = build_url_and_query_string(getsocrata_options)
        print next_url

        next_page = get_socrata_data(getsocrata_options['token'], next_url, getsocrata_options['output_file'])

        # increment the offset regardless of success. "move on"
        getsocrata_options['$offset'] = int(getsocrata_options['$offset']) + int(getsocrata_options['$limit'])

        # skip the write if the request fails, the http_request_history json log file can be used to retry.
        if next_page == None:
            continue
        
        control_iterative_function(getsocrata_options['output_file'], next_page)
    else:

        control_ending_function(getsocrata_options['output_file'], next_page)

def aggregate_arguments():
    """ Get arguments from the command line & configuration file - return the configuration dict as getsocrata_options.

    """


    parser = argparse.ArgumentParser(description='Assign a target URL and an output project or filename.')
    parser.add_argument('--url', type=str, help='source URL')
    parser.add_argument('--outfile', type=str, help='name of output file') # generated from project+timestamp unless specified.
    parser.add_argument('--token', type=str, help='app token')
    parser.add_argument('--config', type=str, help='specify a configuration file')
    parser.add_argument('--project', type=str, help='specify a project name for output')
    
    args = parser.parse_args()


    # Load getsocrata_options from a configration file.
    # Warning: you really should specify an args.config if you are using the "if name == '__main__'" code block.
    if args.config != None:
        getsocrata_options = parse_config_file(args.config)
    else:
        print "Warning: Running this module as __main__ generally requires a configuration file."
        pass


    # TAR 062214 - This area should be generalized using args.__dict__ and a loop.
    # (This is the same effect as vars(args)). This will ensure that all argument 
    # objects that are not None override all config options. (With the added effect 
    # of removing the explicit arguments, generalizing the code)
    #
    # Explicitly define argparse options and override configuration file settings.
    # Don't change these if statements, the user should be able to pass an empty string.
    if args.url != None:
        getsocrata_options['url'] = args.url
    if args.token != None:
        getsocrata_options['token'] = args.token
    if args.project != None:
        getsocrata_options['project'] = args.project
    if args.outfile != None:
        getsocrata_options['output_file'] = args.outfile
    
    # Make sure the required options exist.
    if 'url' not in getsocrata_options:
        raise MissingArgumentException("No URL specified!")
    if 'token' not in getsocrata_options:
        raise MissingArgumentException("No app token specified!")
    
    # SoQL has some defaults which should be respected if unspecified by the user.
    # Two defaults in socrata, these must be defined to allow __main__ to auto-increment by default.
    if '$offset' not in getsocrata_options:
        getsocrata_options['$offset'] = 0
    if '$limit' not in getsocrata_options:
        getsocrata_options['$limit'] = 1000

    # It is preferred not to specify an output file but the functionality is provided.
    # All file writes are appends, so you can do this to merge multiple queries in one file.
    if 'output_file' not in getsocrata_options:
        if 'project' in getsocrata_options:
            getsocrata_options['output_file'] = generate_filename(getsocrata_options['project'])
        else:
            getsocrata_options['output_file'] = generate_filename() # use default value

    return getsocrata_options


def pass_function(*args):
    """ Generic passing function

    """

    pass


def dump_listofdicts_to_pickle(output_file, socrata_page):
    """ One of a selection of functions designed to finish storing data.

    """

    ## Temporary location for pickle logic.
    with open(output_file+".pickle", "w+") as f:
        pickle.dump(gl_total_list, f)
    ## Temporary location for pickle logic.


def write_socrata_page_to_file(output_file, socrata_page):
    """ One of a selection of functions to store the retrieved data.

    """

    # write one json object per line (contains <$limit> records)
    with open(output_file, "a+") as f:
        for each in socrata_page:
            f.write(json.dumps(each) + os.linesep)


def store_socrata_page_in_global_list(output_file, socrata_page):
    """ One of a selection of functions to store the retrieved data.

    """

    gl_total_list.extend(socrata_page)


if __name__ == '__main__':
    """Provide command line options for running this library from the command line.
    
    This module uses a config file parsed by SafeConfigParser. The config file can specify 
    any variable used in argparse, but argparse will override SafeConfigParser. However, 
    the config file MUST be passed as an argument in __main__ or it will not be used.

    REQUIRED COMMAND LINE OPTIONS to run this library from the command line: url, token, config
    """

    getsocrata_options = aggregate_arguments()

    # Control logic for __main__:
    # This function passes functions which describe how to store the data.
    increment_offset_and_record_data_until_empty(write_socrata_page_to_file, pass_function)
    #increment_offset_and_record_data_until_empty(store_socrata_page_in_global_list, dump_listofdicts_to_pickle)

    

