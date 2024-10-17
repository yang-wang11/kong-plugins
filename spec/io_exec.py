import asyncio
import datetime
import logging
import subprocess
import sys
import time
import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Type, Union, Tuple

DEFAULT_10_MINUTES = 600  # default for timeout= argument for subprocess io calls

logger = logging.getLogger(__name__)


class RetryBackOff:
    """
    A class used to implement a backoff algorithm for function retries

    Attributes
        use_exponential_backoff : bool
            a toogle that represent use of exponential-backoff algorithm.
            The exponent-base in case of exponential-backoff is 2
        base_wait_time : int
            base wait period in seconds in case of non-exponential backoff.
            In case of exponential backoff this serves as a multiplication factor.
        wait_incr : int
            amount to increase the base_wait_time in case of non-exponential-backoff
        max_wait_time : int
            the maximum backoff wait period in both exponential/non-exponential cases
        sleep_time : float
            the exact amount of time to sleep on backoff

    Methods
        get_wait_time()
            Return the current wait_period in seconds based on the current retry count
        sleep()
            Sleep sleep_time amount of time based on the retry count
    """

    def __init__(
        self,
        use_exponential_backoff: bool = True,
        base_wait_time: int = 5,
        wait_incr: int = 5,
        max_wait_time: int = 120,
    ) -> None:

        self.use_exponential_backoff = use_exponential_backoff
        self.base_wait_time = base_wait_time
        self.wait_incr = wait_incr if wait_incr is not None else base_wait_time
        self.max_wait_time = max_wait_time

    def get_wait_time(self, retry_count: int) -> int:
        """
        Calculate and return the backoff wait_period in seconds based
        on the exponential_backoff toogle and the current retry count
        retry_count argument should be a positive integer.
        Exception will be raise otherwise.

        """
        if retry_count <= 0:
            raise ValueError('retry_count should be a positive number')

        if self.use_exponential_backoff:
            sleep_time = self.base_wait_time * (2 ** (retry_count - 1))
        else:
            sleep_time = self.base_wait_time + (retry_count - 1) * self.wait_incr

        return min(sleep_time, self.max_wait_time)

    def sleep(self, retry_count: int) -> None:
        """Back off and sleep for sleep_time seconds"""

        sleep_time = self.get_wait_time(retry_count)
        time.sleep(sleep_time)


def kubectl(configpath, params, wait=2, max_tries=3, **kwargs):
    stdin = open("/stdin", "r") if have_stdin() else None
    return try_io(
        cmd=subprocess.check_output,
        pargs=[f"kubectl --kubeconfig={configpath} " + " ".join(params)],
        stdin=stdin,
        shell=True,
        to_catch=subprocess.CalledProcessError,
        suppress_output=True,
        wait=wait,
        max_tries=max_tries,
        timeout=DEFAULT_10_MINUTES,
        **kwargs,
    ).decode("utf-8")


def have_stdin() -> bool:
    try:
        open("/stdin", "r")
    except OSError:
        return False
    return True


def sanitize_arg_string(pargs: Any, kwargs: Dict[str, Any]) -> str:
    """ Function called by try_io to construct the sanitized args string
    from pargs and kwargs. Needed for error messages
    """

    args = ""
    for arg in pargs:
        if isinstance(arg, str):
            args += f'"{arg}",'
        else:
            args += f"{str(arg)},"
    for key, value in kwargs.items():
        if str(key) == "password":
            args += f"{str(key)}=*****,"
        else:
            if isinstance(value, str):
                args += f'{str(key)}="{value}",'
            else:
                args += f"{str(key)}={str(value)},"
    return args[:-1]


def sanitize_kubectl_output(output: str) -> str:
    """ Function called by try_kubectl to sanitize failure output.
    Sanitize the output of a subprocess failure and return it.

    Parameters
        output : str
            The output string from a subprocess
    """

    structured_error_message: str = ""

    if "Kind=Secret" in output and "Error from server: error when applying patch:" in output:
        lines: List[str] = output.split("\n")
        for line in lines:
            if "Name" in line and "Namespace" in line:
                structured_error_message = "Error from server: error when applying patch for Secret: " + line

    if not structured_error_message:
        # return the given string as is because no data was deemed to be redacted
        structured_error_message = output

    return structured_error_message


def try_kubectl(
    cmd: Callable=subprocess.check_output,
    pargs: Optional[List[str]]=None,
    to_catch: Union[Type[Exception], Tuple[Type[Exception]]]=subprocess.CalledProcessError,
    suppress_output: bool=True,
    shell: bool=True,
    wait: int=5,
    max_tries: int=12,
    timeout: int=DEFAULT_10_MINUTES,
    exponential_backoff: bool=True,
    write_errors_in_sdterr: bool=True,
    **kwargs
) -> Union[int, str]:
    """This function sets a number of default args with presets that are usually applied to kubectl commands"""

    pargs = pargs if pargs is not None else []

    stderr = kwargs.pop("stderr", None)
    if stderr is None:
        stderr = subprocess.STDOUT

    try:
        result = try_io(
            cmd=cmd,
            pargs=pargs,
            to_catch=to_catch,
            suppress_output=suppress_output,
            shell=True,
            stderr=stderr,
            wait=wait,
            max_tries=max_tries,
            timeout=timeout,
            exponential_backoff=exponential_backoff,
            **kwargs,
        )
    except to_catch as e:
        if write_errors_in_sdterr:
            # Redact secret data in case of an error
            output: str = sanitize_kubectl_output(e.output.decode("utf-8")) if e.output else ""
            sys.stderr.write(output)
        raise e

    if cmd == subprocess.check_output:
        return result.decode("utf-8")
    return result


def try_kubectl_with_server_side_apply(
    cmd: Callable=subprocess.check_output,
    pargs: Optional[List[str]]=None,
    to_catch: Union[Type[Exception], Tuple[Type[Exception]]]=subprocess.CalledProcessError,
    suppress_output: bool=True,
    shell: bool=True,
    wait: int=5,
    max_tries: int=12,
    timeout: int=DEFAULT_10_MINUTES,
    exponential_backoff: bool=True,
    **kwargs
) -> Union[int, str]:
    """Adds args --server-side --force-conflicts to try_kubectl call"""
    new_pargs = [pargs[0] + " --server-side --force-conflicts"]
    return try_kubectl(
        cmd=cmd,
        pargs=new_pargs,
        to_catch=to_catch,
        suppress_output=suppress_output,
        shell=shell,
        wait=wait,
        max_tries=max_tries,
        timeout=timeout,
        exponential_backoff=exponential_backoff,
        **kwargs
    )


def try_io(
    cmd=print,
    pargs: Optional[Any]=None,
    to_catch: Union[Type[Exception], Tuple[Type[Exception]]]=Exception,
    on_error: Optional[Callable[[Exception], None]]=None,
    retry_voter: Optional[Callable[[Exception], bool]]=None,
    suppress_output: bool=False,
    wait: int=5,
    max_tries: int=5,
    wait_incr: None=None,
    exponential_backoff: bool=False,
    **kwargs
) -> Any:
    """
    Generic function that retries operation "cmd" "max_tries" number of times
    and waits between attempts "wait" seconds.

    If it is supplied, "on_error" will be invoked with the caught-exception, but only if retries are left.

    If it is supplied, "retry_voter" will be invoked with the caught-exception, and can return False to abort the operation.

    Positional arguments must be passed in as an array like
    pargs = ["arg1", "arg2", "arg3", ...]
    Key value arguments are passed in as they would be to cmd
    """

    retry_backoff = RetryBackOff(
        use_exponential_backoff=exponential_backoff,
        base_wait_time=wait,
        wait_incr=wait_incr,
    )

    pargs = pargs if pargs is not None else []
    args = sanitize_arg_string(pargs, kwargs)

    for try_count in range(1, max_tries + 1):
        try:
            result = cmd(*pargs, **kwargs)  # The * operator expands the list
            return result

        # Following are typically coding errors - do not retry entire operations if these occur
        except (ArithmeticError, LookupError, TypeError, AssertionError):
            raise

        except to_catch as e:
            if try_count == max_tries:
                raise e

            # Call 'on_error' function if one is provided if only there are retries left
            if on_error is not None:
                on_error(e)

            # Check if callback function (retry_voter) is given and votes to abort the retry mechanism (returns False)
            if retry_voter is not None and retry_voter(e) is False:
                raise e

            wait_time = retry_backoff.get_wait_time(try_count)
            if not suppress_output:
                logger.warning(
                    f"Caught {type(e).__name__} while executing the command: {cmd}({args}): {str(e)}. Trying again ({try_count+1}/{max_tries}) after {wait_time} s..."
                )
            retry_backoff.sleep(try_count)


def repeat_until_success(minutes: int, sleep_seconds: int=60.0, only_retry_on: Optional[Exception]=None):
    """
    Decorator to repeat a function until it succeeds.
    If an exception is given as `only_retry_on` and the exception has occurred, the function will be re-tried.
    All other type of exceptions will be raised instantly.
    By default, the function retries the calling-function on all caught Exceptions.

        Parameters:
        -----------
            minutes: `int`
            sleep_seconds: `float`
            only_retry_on: `Optional[Exception]`

    """

    def wait_loop(function):
        if minutes <= 0:
            @functools.wraps(function)
            def raiser(*args, **kwargs):
                raise Exception(f"minutes({minutes}) of repeat_until_success must be larger than 0")
            return raiser
        def wrapper(*args, **kwargs):
            time_to_stop = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            do_it_again = False
            retry_count = 0
            retry_duration_seconds = 0
            time_to_start = datetime.datetime.now()
            frm = inspect.stack()[1].function
            while do_it_again or datetime.datetime.now() < time_to_stop:
                try:
                    retry_duration_seconds = (datetime.datetime.now() - time_to_start).seconds
                    result = function(*args, **kwargs)
                    if retry_count:
                        info = f"{frm} call {function.__name__} with repeat_until_success(minutes={minutes}, sleep_seconds={sleep_seconds}), retry_count: {retry_count}, retry_duration_seconds: {retry_duration_seconds}"
                        logger.info(info)
                    return result
                except Exception as e:  # pylint: disable=broad-except, invalid-name
                    if only_retry_on:
                        do_it_again = not is_timeout_reached(time_to_stop) and isinstance(e, only_retry_on)
                    else:
                        do_it_again = not is_timeout_reached(time_to_stop)

                    if not do_it_again:
                        if only_retry_on and not isinstance(e, only_retry_on):
                            error_message = f"raising exception without retries (exception is no instance of '{only_retry_on}')"
                        elif retry_count < 1:
                            error_message = "raising exception without retries"
                        else:
                            error_message = f"raising exception after retrying {retry_count} times ({minutes} minutes waited)"
                        logger.warning(error_message)
                        raise e
                time.sleep(sleep_seconds)
                retry_count = retry_count + 1

        return wrapper
    return wait_loop


def is_timeout_reached(time_to_stop):
    return datetime.datetime.now() >= time_to_stop


def repeat_until_success_async(minutes, sleep_seconds=60.0):
    """ decorator to repeat a function until it succeeds for async function """

    def wait_loop(function):
        if minutes <= 0:
            @functools.wraps(function)
            def raiser(*args, **kwargs):
                raise Exception(f"minutes({minutes}) of repeat_until_success_async must be larger than 0")
            return raiser
        async def wrapper(*args, **kwargs):
            time_to_stop = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            do_it_again = False
            while do_it_again or datetime.datetime.now() < time_to_stop:
                try:
                    return await function(*args, **kwargs)
                except Exception as e:  # pylint: disable=broad-except, invalid-name
                    if datetime.datetime.now() < time_to_stop:
                        do_it_again = True  # prevent timing issue
                    else:
                        raise e
                await asyncio.sleep(sleep_seconds)
        return wrapper
    return wait_loop
