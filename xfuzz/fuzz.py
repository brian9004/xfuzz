import aiohttp
import sys
import asyncio

match_code = []

async def fuzz(args):
    """Fuzz a target URL with the command-line arguments specified by ``args``."""
    global match_code
    match_code = args.match_codes
    # TODO: your code here!
    foundInURL = False
    foundInData = False
    foundInHeader = False

    # For -w, text file from installation instructions (common.txt)
    w_list = []
    if args.wordlist == '-':
        for line in sys.stdin:
            w_list.append(line.strip('\n'))
    else:
        f = open(args.wordlist, 'r')
        for line in f:
            w_list.append(line.strip('\n'))

    # For -u, http URL followed by FUZZ url
    # For -e, extension part off of the FUZZ (replace word in the wordlist with)
    if "FUZZ" in args.url:
        foundInURL = True

    url_list = []
    if len(args.extensions) != 0:
        for w in w_list:
            for ext in args.extensions:
                url_list.append(args.url.replace("FUZZ", w + ext))
    else:
        for w in w_list:
            url_list.append(args.url.replace("FUZZ", w))

    # For -H, headers
    if len(args.headers) != 0:
        h_dictlist = []
        for h in args.headers:
            if "FUZZ" in h:
                foundInHeader = True
            temp = h.replace(' ', '').split(':')
            for w in w_list:
                h_dictlist.append({temp[0].replace("FUZZ", w): temp[1].replace("FUZZ", w)})
        args.headers = h_dictlist
    else:
        args.headers = [{}]

    # For -d, data
    data_list = []
    if args.data is not None:
        if "FUZZ" in args.data:
            foundInData = True
        for w in w_list:
            data_list.append(args.data.replace("FUZZ", w))

    master_dict = []
    if foundInURL:
        for url in url_list:
            cur_dict = {'url': url, 'method': args.method, 'data': args.data, 'headers': args.headers[0]}
            master_dict.append(cur_dict)
    elif foundInData:
        for d in data_list:
            cur_dict = {'url': args.url, 'method': args.method, 'data': d, 'headers': args.headers[0]}
            master_dict.append(cur_dict)
    elif foundInHeader:
        for dict_ in args.headers:
            cur_dict = {'url': args.url, 'method': args.method, 'data': args.data, 'headers': dict_}
            master_dict.append(cur_dict)

    # Perform some pre-processing here with input arguments...
    work_queue = asyncio.Queue()
    tasks = []

    # Create a scheduler task to queue up jobs
    s = asyncio.create_task(scheduler(work_queue, master_dict))
    tasks.append(s)

    # Create workers to consume jobs
    for _ in range(10):
        w = asyncio.create_task(start_worker(work_queue))
        tasks.append(w)

    # Wait for the scheduler and the workers to finish
    await asyncio.gather(*tasks)


async def scheduler(queue, jobs):
    # Put jobs onto the queue so that workers can execute them
    for job in jobs:
        await queue.put(job)  # Put a single dictionary from master_dict onto queue

    # Put None onto the queue once for each worker so that they know
    # there isn't any more work to do
    for _ in range(10):
        await queue.put(None)


async def start_worker(queue):
    while True:
        # Get some new work off the queue
        job = await queue.get()

        try:
            # If the job is `None`, there's no more work to do, so the
            # worker can exit
            if job is None:
                break
            async with aiohttp.ClientSession() as session:
                async with session.request(job['method'], job['url'], data=job['data'], headers=job['headers']) as resp:
                    if resp.status in match_code:
                        print(f"{job['url']} - Status {resp.status}")

        finally:
        # Mark the job as being completed
            queue.task_done()