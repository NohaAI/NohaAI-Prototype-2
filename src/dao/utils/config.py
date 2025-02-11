from configparser import ConfigParser
def load_simple_connection_config():
    config=load_config()
    simple_connection_config={
        'host': config['host'],
        'dbname': config['database'],
        'user': config['user'],
        'password': config['password'],
        'port': 5432  
    }
    return simple_connection_config

def load_config(filename='src/dao/utils/database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config

if __name__ == '__main__':
    simple_connection_config = load_simple_connection_config()
    print(simple_connection_config)