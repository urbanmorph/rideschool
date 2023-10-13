# config.py module is used for reading configuration values from config.txt




#Inside the config.py module, we should put the code for reading and parsing the config.txt configuration file and defining a function to access the configuration values. Here's the code you should put inside config.py:


config = {} # Create an empty dictionary to store configuration values

# Read and parse the configuration file
with open('config/config.txt', 'r') as config_file:
    #This line opens the file config.txt located in the config directory in read ('r') mode. The with statement is used to ensure that the file is properly closed after it's been read. It also assigns the opened file to the variable config_file.
    for line in config_file:
        # This line iterates through each line of the opened config_file. It reads the file line by line.
        key, value = line.strip().split('=') #For each line, it does the following:
        #line.strip(): Removes any leading or trailing whitespace (like spaces or newline characters) from the line.
        #  Splits the line into two parts at the equal sign (=). The part before the equal sign is assigned to the variable key, and the part after the equal sign is assigned to the variable value. In configuration files, this is a common format used to define key-value pairs.
        config[key] = value
        #After splitting the line into key and value, it stores them as a key-value pair in a Python dictionary called config. This dictionary is used to hold the configuration values for your application.
        #config is the  dictionary that  is used to hold the configuration values for the  application.

# Example function to access configuration values
def get_config_value(key, default=None):# Python function named get_config_value that allows you to access configuration values from the config dictionary, which was populated with key-value pairs from the config.txt file.
    #This line defines the function. It takes two arguments:
    # key: This is the key for the configuration value you want to retrieve. 
    #default=None: This is an optional argument that provides a default value , If key is not found, the function will return default.if the specified key doesn't exist in the configuration. If key is not found, the function will return default.
    return config.get(key, default)
#If key is not found, the function will return default.