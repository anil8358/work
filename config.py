import gallifrey
aws_env = gallifrey.AWSEnvironment()
# Application settings
APPLICATION_NAME = 'gossip-bot'
LOG_FILE_NAME = APPLICATION_NAME + '.log'  # Log file directory is as per gallifrey configuration
tardis_inst = gallifrey.Tardis()
elasticSearchURI = tardis_inst.get_resource_url("ElasticSearchAWSInstance")
AWSRegion = aws_env.get_region()