
getsocrata
------
When used as main() the returned json pages are saved in append mode as they are retrieved.  They are saved as lines of json serializable objects.  To load the resulting file, do so line-by-line with json.loads().

Python 3 support is expected in the future but not begun.

Getting Started:
------

getsocrata was written in Python 2 and will need some tweaks to be run in python3.  


1. Get the socrata json endpoint for your data. This is a URL (ex - http://data.sfgov.org/resource/7h4w-reyq.json)    
2. Register with Socrata at https://opendata.socrata.com/login and get an app token. You'll use this to access your private rate limit. Basic steps: Create an account -> login to your account -> Edit account settings -> App Tokens -> Create new application -> Copy your App token    
3. Move 'key.sh.auth.template' to 'key.sh.auth'. Add your app token as "<app token>".    
4. Modify sample.config to contain your  url(endpoint), and any filters or SoQL Queries (see the Socrata SODA API documentation).    
5. Use requirements.txt to build an appropriate virtual environment: pip install -r requirements.txt    
6. Run ./example.sh from bash.    


Python help() Output:
------

Python help built-in function on module getsocrata:

NAME
    getsocrata - Run with the -h argument for help.

FILE
    /home/robbintt/monolith/getsocrata/getsocrata.py

DESCRIPTION
    This module may be run from the command line or may be imported into a larger project.
    
    The module uses Socrata Open Data Api (SODA) Version 1
    This uses the deprecated authentication format with no callback URL. Socrata may 
    discontinue this request type in the future in favor of a callback URL method.

CLASSES
    exceptions.Exception(exceptions.BaseException)
        MissingArgumentException
    
    class MissingArgumentException(exceptions.Exception)
     |  Exception class for when a critical argument is not passed before it is needed.
     |  
     |  Method resolution order:
     |      MissingArgumentException
     |      exceptions.Exception
     |      exceptions.BaseException
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self, value)
     |  
     |  __str__(self)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes inherited from exceptions.Exception:
     |  
     |  __new__ = <built-in method __new__ of type object>
     |      T.__new__(S, ...) -> a new object with type S, a subtype of T
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from exceptions.BaseException:
     |  
     |  __delattr__(...)
     |      x.__delattr__('name') <==> del x.name
     |  
     |  __getattribute__(...)
     |      x.__getattribute__('name') <==> x.name
     |  
     |  __getitem__(...)
     |      x.__getitem__(y) <==> x[y]
     |  
     |  __getslice__(...)
     |      x.__getslice__(i, j) <==> x[i:j]
     |      
     |      Use of negative indices is not supported.
     |  
     |  __reduce__(...)
     |  
     |  __repr__(...)
     |      x.__repr__() <==> repr(x)
     |  
     |  __setattr__(...)
     |      x.__setattr__('name', value) <==> x.name = value
     |  
     |  __setstate__(...)
     |  
     |  __unicode__(...)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from exceptions.BaseException:
     |  
     |  __dict__
     |  
     |  args
     |  
     |  message

FUNCTIONS
    build_url_and_query_string(getsocrata_options)
        Builds url string from user provided socrata SODA api parameters.
        
        Question: Can URL QueryStrings be ordered? Does the order matter? Does socrata need the order or respect the order?
    
    generate_filename(filename_base='myproject')
        Use a timestamp and an optional project name to make a unique filename.
    
    get_socrata_data(user_auth, source_url, output_file)
        Retrieve and turn a list of json objects (records) from a socrata API endpoint.
        
        This specific setup has been tested on SFgov's Socrata API.
        
        This uses the deprecated authentication format with no callback URL. Socrata may 
        discontinue this request type in the future in favor of a callback URL method.
    
    increment_offset_and_record_data_until_empty()
        This control loop iteratively pulls data until it runs out
    
    parse_config_file(config_filename)
        Load a configuration file into the configuration dict and return it.
        
        This is really just a controller function for using the generic retrieve_config() function.
    
    retrieve_config(config_filename='simple.config', section='getsocrata')
        Read and return configuration values from a configuration file.
        
        This is a generic function for moving key-value pairs from a ConfigParser config file into a dictionary.

DATA
    getsocrata_options = {}
    http_request_history = {}


None
