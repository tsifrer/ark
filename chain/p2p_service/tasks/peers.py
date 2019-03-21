from .config import huey


@huey.task()
def count_beans(num):
    print('-- counted %s beans --' % num)
