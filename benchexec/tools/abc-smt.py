# This file is part of BenchExec, a framework for reliable benchmarking:
# https://github.com/sosy-lab/benchexec
#
# SPDX-FileCopyrightText: 2007-2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import benchexec.util as util
import benchexec.tools.smtlib2
import benchexec.result as result


class Tool(benchexec.tools.smtlib2.Smtlib2Tool):
    """
    Tool info for ABC solver.
    """

    def executable(self):
        return util.find_executable("runner-abc.sh")

    def version(self, executable):
        line = self._version_from_tool(executable, "-version")
        return line.strip()

    def name(self):
        return "abc"

    def cmdline(self, executable, options, tasks, propertyfile=None, rlimits={}):
        assert len(tasks) <= 1, "only one inputfile supported"
        return [executable] + options + tasks

    def determine_result(self, returncode, returnsignal, output, isTimeout):

        if returnsignal == 0 and returncode == 0 or returncode == 1:
            status = None
            for line in output:
                line = line.strip()
                if line == "sat":
                    status = result.RESULT_TRUE_PROP
                elif line == "unsat":
                    status = result.RESULT_FALSE_PROP
                elif not status and line.startswith("(error "):
                    status = "ERROR"

            if not status:
                status = result.RESULT_UNKNOWN

        elif ((returnsignal == 9) or (returnsignal == 15)) and isTimeout:
            status = "TIMEOUT"

        elif returnsignal == 9:
            status = "KILLED BY SIGNAL 9"
        elif returnsignal == 6:
            status = "ABORTED"
        elif returnsignal == 15:
            status = "KILLED"
        else:
            status = f"ERROR ({returncode})"

        return status