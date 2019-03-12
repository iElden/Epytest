import subprocess
import signal

SUCESS = "OK"
FAIL_RT = "FAIL (invalid return code)\nexcepted:\n{}\ngot:\n{}"
FAIL_SO = "FAIL (invalid output)\nexcepted:\n{}\ngot:\n{}"
FAIL_SE = "FAIL (invalid error output)\nexcepted:\n{}\ngot:\n{}"
CRASH = "CRASH !\nProgramm returned code : {} ({})"


def execute_test(binary_name=None, args=[], stdin=None,
                 ex_stdout=None, ex_stderr=None, ex_return_code=None,
                 timeout=None, cmd=None, shell=None, name=None, login=None):
    r = subprocess.run(cmd or ([login + binary_name] + args), text=True, input=stdin,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=timeout, shell=shell if shell is not None else bool(cmd))
    if r.returncode < 0:
        return CRASH.format(abs(r.returncode) + 128, signal.Signals(abs(r.returncode)).name)
    if ex_return_code is not None and ex_return_code != r.returncode:
        return FAIL_RT.format(ex_return_code, r.returncode)
    if ex_stdout is not None and ex_stdout != r.stdout:
        return FAIL_SO.format(ex_stdout, r.stdout)
    if ex_stderr is not None and ex_stderr != r.stderr:
        return FAIL_SE.format(ex_stderr, r.stderr)
    else:
        return SUCESS
