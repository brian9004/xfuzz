import aiohttp
import sys


async def fuzz(args):
    """Fuzz a target URL with the command-line arguments specified by ``args``."""

    # TODO: your code here!

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
    url_list = []
    if len(args.extensions) != 0:
        for w in w_list:
            for ext in args.extensions:
                url_list.append(args.url.replace("FUZZ", w + ext))
    else:
        for w in w_list:
            url_list.append(args.url.replace("FUZZ", w))
    #print(url_list)

    # For -H, headers
    if len(args.headers) != 0:
        h_dict = {}
        for h in args.headers:
            temp = h.replace(' ', '').split(':')
            for w in w_list:
                h_dict[temp[0].replace("FUZZ", w)] = temp[1].replace("FUZZ", w)
        args.headers = h_dict
    else:
        args.headers = {}

    # For -d, data
    data_list = []
    if args.data is not None:
        for w in w_list:
            data_list.append(args.data.replace("FUZZ", w))

    # ex: print the arguments that were passed in to this function
    print(f"args = {args}")

    # For -X, request type (GET, POST)
    # For -mc, process matchcodes
    # Replace do_work_for_job with this
    # ex: make an HTTP request to the input URL

    if len(url_list) != 0:
        for url in url_list:
            async with aiohttp.ClientSession() as session:
                async with session.request(args.method, url, data=args.data, headers=args.headers) as resp:
                    if resp.status in args.match_codes:
                        print(f"{url} - Status {resp.status}")
    elif len(data_list) != 0:
        for d in data_list:
            async with aiohttp.ClientSession() as session:
                async with session.request(args.method, args.url, data=d, headers=args.headers) as resp:
                    if resp.status in args.match_codes:
                        print(f"{args.url} - Status {resp.status}")
    else:
        async with aiohttp.ClientSession() as session:
            async with session.request(args.method, args.url, data=args.data, headers=args.headers) as resp:
                if resp.status in args.match_codes:
                    print(f"{args.url} - Status {resp.status}")
