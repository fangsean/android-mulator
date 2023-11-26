import multiprocessing
from typing import Dict, List, Callable, Any
from logging import getLogger


LOG = getLogger()


def yield_items(items: List[Any], num: int = 10):
    ''' make chunks of max 10 items from a list of sqs queue items

    Args:
        items (list): a list with sqs queue items
        num (int): number of items which should be yielded

    Yield:
        (generator): a yield generator with chunks of max 10 queue items
    '''
    for i in range(0, len(items), num):
        yield items[i:i + num]

def multiprocessing_collect(items: List[Dict], function: Callable,
                            chunks: int = 10, **kwargs) -> List[Dict]:
    '''

    Args:
        items (List): A list with items
        function (): The target python method that is collection the details
        chunks (int): The number of items that should be processed by a single
            process

    Returns:
        (List):
    '''
    LOG.debug('Start collecting details via multiprocessing')

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    item_details = []
    processes = []

    # Split the list of items into smaller chunks
    chunks = yield_items(items=items, num=chunks)

    # Prepare each single process for the execution
    for index, list_chunk in enumerate(chunks):
        process = multiprocessing.Process(
            target=function,
            args=(index, list_chunk, return_dict),
            kwargs=kwargs,
        )

        processes.append(process)

    # Start all processes
    for process in processes:
        process.start()

    # Make sure that all processes have finished
    for process in processes:
        process.join()

    # Iterate trough all accounts
    for value in return_dict.values():
        item_details += value

    # Return the item details with the enriched information
    return item_details


def multiprocessing_group(items: List[Dict], function: Callable,
                          chunks: int = 10, **kwargs) -> List[Dict]:
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    item_details = []
    processes = []

    def yield_items(items: List[Any], num: int = 10):
        for item in items:
            # return items[item]
            yield items[item]

    # Split the list of items into smaller chunks
    chunks = yield_items(items=items, num=chunks)

    # Prepare each single process for the execution
    for index, list_chunk in enumerate(chunks):
        process = multiprocessing.Process(
            target=function,
            args=(index, list_chunk, return_dict),
            kwargs=kwargs,
        )

        processes.append(process)

    # Start all processes
    for process in processes:
        process.start()

    # Make sure that all processes have finished
    for process in processes:
        process.join()

    # Iterate trough all accounts
    for value in return_dict.values():
        item_details += value

    # Return the item details with the enriched information
    return item_details

