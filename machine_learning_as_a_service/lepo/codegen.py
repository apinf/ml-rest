import argparse
import sys

import yaml
from six import StringIO
from django.utils.text import camel_case_to_spaces

from lepo.router import Router

HANDLER_TEMPLATE = '''
def {func_name}(request, {parameters}):
    raise NotImplementedError('Handler {operation_id} not implemented')
'''.strip()


def generate_handler_stub(router, handler_template=HANDLER_TEMPLATE):
    output = StringIO()
    func_name_to_operation = {}
    for path in router.get_paths():
        for operation in path.get_operations():
            snake_operation_id = camel_case_to_spaces(operation.id).replace(' ', '_')
            func_name_to_operation[snake_operation_id] = operation
    for func_name, operation in sorted(func_name_to_operation.items()):
        parameter_names = [p['name'] for p in operation.parameters]
        handler = handler_template.format(
            func_name=func_name,
            operation_id=operation.id,
            parameters=', '.join(parameter_names),
        )
        output.write(handler)
        output.write('\n\n\n')
    return output.getvalue()


def cmdline():
    ap = argparse.ArgumentParser()
    ap.add_argument('input', default=None, nargs='?')
    args = ap.parse_args()
    input = (open(args.input) if args.input else sys.stdin)
    api = yaml.safe_load(input)
    print(generate_handler_stub(Router(api)))


if __name__ == '__main__':
    cmdline()
