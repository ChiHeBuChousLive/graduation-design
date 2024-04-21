from django.core.management.base import BaseCommand

from app.models import Car_manage

'''
BaseCommand 是一个自定义管理命令的基类。
这个类提供了处理命令行参数、运行命令以及显示输出的功能和方法。
通过继承 BaseCommand，可以创建自定义的管理命令，用于在 Django 项目中执行特定的任务或操作。
'''


# 这是初始化100个停车位
# python manage.py configure_park 100
# 这是增加100个停车位，注意，这是增加
# python manage.py configure_park 100 --add true


# 用于初始化停车位的数量和增加停车位信息（简单来说就是在数据表中创建插入空值）
class Command(BaseCommand):
    help = '停车场车位信息'

    #这个应该是定义参数的类型
    def add_arguments(self, parser):
        parser.add_argument('num', type=int, help='停车位数量')
        parser.add_argument(
            '--add',
            dest='add',
            help='增加停车位的数量',
        )

    def handle(self, *args, **options):
        num = options['num']  # 增加的数量.option就是命令行后面的数量
        add = options.get('add')  # 初始化还是添加
        #现在数据库插入的位置
        start_mark = 1  # 计数

        #如果有add命令
        if add:
            # 初始化
            if Car_manage.objects.count() == 0:
                start_mark = 1
            # 额外添加
            else:
                start_mark = Car_manage.objects.last().carport + 1

        for i in range(num):
            Car_manage(carnum=None, carport=start_mark, begintime=None, endtime=None, genre=None).save()
            start_mark += 1
        self.stdout.write(self.style.SUCCESS(f'成功创建 {num} 个停车位！'))


