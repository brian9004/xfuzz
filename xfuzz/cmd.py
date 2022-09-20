# Methods for setting up command line argument parsing.

import argparse
import typing as _t
import os

# Default list of HTTP response status codes that we should match if the -mc argument
# is not passed in.
DEFAULT_MATCH_CODES: _t.Final[_t.List[int]] = [200, 301, 302, 401, 403]

# Program description printed out when the -h / --help flag is given
DESCRIPTION: _t.Final[str] = """
Simple web fuzzer using aiohttp
"""

# Parser epilogue. This is displayed after the information about the flags when the
# --help flag is passed in to xfuzz.
#
# **Feel free to change this!** Just keep in mind that these usage instructions reflect
# how the test harness is expecting to use xfuzz.
EPILOGUE: _t.Final[
    str
] = """
-----

EXAMPLES:

  Find all pages under https://example.org/ ending with .php or .html that return an
  HTTP 200 OK response.

    python3 -m xfuzz -w /path/to/wordlist.txt -mc 200 -e php -e html \\
        -u 'https://example.org/FUZZ'

  Find users with some integer UID by fuzzing the `id` URL parameter of a page:

    seq 1 10000 | python3 -m xfuzz -u 'https://example.org/user?id=FUZZ'

  Make POST requests with JSON data to fuzz a login API and brute-force the password
  of the 'admin' user.

    python3 -m xfuzz -w /path/to/password/wordlist.txt -mc 200 -u 'https://example.org/login' \\
        -X POST -H 'Content-Type: application/json' -d '{"username":"admin","password":"FUZZ"}'

You can find more information at https://github.com/kernelmethod/xfuzz
"""


def setup_argument_parser() -> argparse.ArgumentParser:
    """Create a new ``ArgumentParser`` instance to parse command-line arguments
    passed in to the script."""

    # If the COLUMNS environment variable is not set, default to text wrapping at
    # 100 columns.
    os.environ.setdefault("COLUMNS", "100")

    parser = argparse.ArgumentParser(
        prog="xfuzz",
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOGUE,
    )

    # NOTE: you may *not* change any of the command line arguments that are here by
    # default! These are needed to make the tests work correctly.

    # Add required arguments
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="The URL to fuzz",
    )

    # Add optional arguments
    parser.add_argument(
        "-w",
        "--wordlist",
        help=(
            "The wordlist to use (provided as a path to a local file). If not provided, xfuzz will "
            "read from stdin instead."
        ),
    )
    parser.add_argument(
        "-e",
        "--extension",
        action="append",
        help=("One or more extensions to append (e.g. php, html, etc.). Multiple extensions " "may be provided."),
    )
    parser.add_argument(
        "-X",
        "--method",
        default="GET",
        help="HTTP method to use (GET, POST, PUT, etc.) (default: %(default)s)",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        help=(
            'One or more HTTP headers to add to requests, in the form "HeaderName: HeaderValue" '
            '(e.g. "Content-Type: application/json" or `"Host: FUZZ.example.com"`). May be '
            "specified one or more times."
        ),
    )
    parser.add_argument("-d", "--data", help="Data to send in the body of the HTTP request.")
    parser.add_argument(
        "-mc",
        type=int,
        action="append",
        help=(
            "Match HTTP response codes. May be specified multiple times. If let unspecified, "
            f"defaults to the following response codes: {DEFAULT_MATCH_CODES}"
        ),
    )

    # TODO: add any additional (optional) arguments that you want! However, note that these
    # arguments will not be explicitly supplied to the program during testing.

    return parser


def parse_args(argv=None) -> argparse.Namespace:
    """Parse command-line arguments and return them in an ``argparse.Namespace`` instance."""

    # NOTE: do *not* edit this function! The test harness expects arguments to be passed in to
    # the fuzz() function in a certain way.

    parser = setup_argument_parser()
    args = parser.parse_args(args=argv)

    # Set defaults for arguments with action="append"
    args.extensions = [] if args.extension is None else [f".{ext}" for ext in args.extension]
    args.headers = [] if args.header is None else args.header
    args.mc = DEFAULT_MATCH_CODES if args.mc is None else args.mc

    return args
