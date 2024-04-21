import os
import sys


def main():
    #导入了模型和setting
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Park.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django环境异常，请检查！"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
