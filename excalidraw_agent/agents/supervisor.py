from loguru import logger

def supervisor(state, llm=None):

    #print("Supervisor: analyzing request")
    logger.info("Supervisor: analyzing request...")
    logger.add('./LOGS/logs.log', rotation="500 MB", retention="10 days")

    return state