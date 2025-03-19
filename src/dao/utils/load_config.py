from configparser import ConfigParser

def load_database_config(filename='src/config/database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    # Get section, default to postgresql
    if not parser.has_section(section):
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    # Extract parameters into a dictionary
    config = {param[0]: param[1] for param in parser.items(section)}

    # Create the simple connection config with required fields
    connection_config = {
        'host': config['host'],
        'dbname': config['database'],
        'user': config['user'],
        'password': config['password'],
        'port': 5432  
    }
    
    return connection_config

if __name__ == '__main__':
    connection_config = load_database_config()