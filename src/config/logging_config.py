# Logging configurations

### Example 

# import logging

# LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# logging.basicConfig(
#     filename="../../noha_ai_prototype.log",
#     level=logging.INFO,
#     format=LOG_FORMAT,
# )

###
# Toggle ENABLE_LOGGING to enable/disable logging. 
# note: This only disables logging output; logging calls will still be executed. To eliminate latency from log statements, remove them from the production code.

ENABLE_LOGGING = True  
