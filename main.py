import argparse
import os
import subprocess

from _logging_config import script_logger_root
from action.abstract import InitBasedAction, RunAction

current_dir = os.path.dirname(os.path.realpath(__file__))
bat_file = os.path.join(current_dir, "init.bat")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='IP of virtual machines',  default='127.0.0.1', type=str, nargs='?')
    parser.add_argument('--first', help='first port Number of virtual machines',  default=16384, type=int, nargs='?')
    parser.add_argument('--num', help='Number of virtual machines',  default=1, type=int, nargs='?')
    parser.add_argument('--action', help='Print verbose log (debug level) to screen', choices=['init', 'run'], default='init')
    args = parser.parse_args()
    action_dict = {'init': InitBasedAction, 'run': RunAction}
    action_class = action_dict.get(args.action.lower(), None)
    if action_class is None:
        script_logger_root.critical('Unable to find execution action  "%s"' % args.action)
        exit(1)
    script_logger_root.info('Using execution action: %s' % str(action_class))
    host = args.host
    first = args.first
    num = args.num
    result = subprocess.Popen([bat_file, host, str(first), str(num)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print("Bat executed successfully")

    target = action_class(host, num, first)
    try:
        target.handle()
    except Exception as ex:
        ex_type = type(ex)
        script_logger_root.critical(f'Exception while executing script: ({ex_type.__module__}.{ex_type.__qualname__}) '
                                f'"{str(ex)}"', exc_info=ex, stack_info=True)


if __name__ == '__main__':
    main()
