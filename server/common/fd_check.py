import logging
import os
import errno

max_fd = os.sysconf('SC_OPEN_MAX')


def assert_all_fds_are_closed():
    """
    Check that all file descriptors are closed, except for stdin, stdout, and stderr.
    """

    error = False
    for fd in range(3, max_fd):
        try:
            os.fstat(fd)
        except OSError as e:
            if e.errno == errno.ENOENT or e.errno == errno.EBADF:
                continue
            else:
                raise
        else:
            logging.error(f"action: assert_all_fds_are_closed | result: failed | fd: {fd}")
            error = True

    if not error:
        logging.debug(f"action: assert_all_fds_are_closed | result: success")
