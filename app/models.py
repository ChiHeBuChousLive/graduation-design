from django.db import models


# 管理员信息表
class Administrator(models.Model):
    account = models.CharField(max_length=32, primary_key=True)  # 管理员账号
    password = models.CharField(max_length=32)  # 密码

    # 设置表名称
    class Meta:
        db_table = "admin"


# 用户信息表
class User(models.Model):
    name = models.CharField(max_length=32, verbose_name='姓名')
    carnum = models.CharField(max_length=32, unique=True, verbose_name='车牌号')
    phone = models.CharField(max_length=32, verbose_name='手机号')
    level = models.IntegerField(verbose_name='会员套餐')
    #开始时间，结束时间
    begintime = models.DateTimeField(auto_now=False, auto_now_add=False)
    endtime = models.DateTimeField(auto_now=False, auto_now_add=False)

    # 设置表名称
    class Meta:
        db_table = "user"


# 车位信息表
class Car_manage(models.Model):
    carnum = models.CharField(max_length=32, unique=True, null=True, verbose_name='车牌号')
    carport = models.IntegerField(verbose_name='车位')
    begintime = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    endtime = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    genre = models.IntegerField(verbose_name='种类', null=True)

    # 设置表名称
    class Meta:
        db_table = "car_manage"

# 车位动态测试表
class Car_manage_test(models.Model):
    carnum = models.CharField(max_length=32, unique=True, null=True, verbose_name='车牌号')
    carport = models.IntegerField(verbose_name='车位')
    begintime = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    endtime = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    genre = models.IntegerField(verbose_name='种类', null=True)
    parking= models.BooleanField(default=False,verbose_name='是否存在车辆')
    pos=models.CharField(max_length=32,unique=False,null=True,verbose_name='位置')
    # 设置表名称
    class Meta:
        db_table = "car_manage_test"

# 停车记录
class Car_record(models.Model):
    carnum = models.CharField(max_length=32, verbose_name='车牌号')
    begintime = models.DateTimeField(auto_now=False, auto_now_add=False)
    endtime = models.DateTimeField(auto_now=False, auto_now_add=False)
    #是不是会员
    genre = models.IntegerField(verbose_name='种类')
    money = models.IntegerField(verbose_name='收费')

    # 设置表名称
    class Meta:
        db_table = "car_record"


# 车牌信息表
# 记录来过了的而系统的所有的车牌
class License_plate(models.Model):
    car_img = models.ImageField(upload_to='car_imgs', unique=True, blank=True, null=True)
    car_num = models.CharField(max_length=32, unique=True, verbose_name='车牌号', null=True)
    #是否还在停车场里面
    is_inside = models.BooleanField(default=False)

    # 设置表名称
    class Meta:
        db_table = "license_plate"


# 支付信息表
class Charge(models.Model):
    pay_time = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    money = models.IntegerField(verbose_name='收费')

    # 设置表名称
    class Meta:
        db_table = "charge"


# 停车信息
class Car_in_record(models.Model):
    carnum = models.CharField(max_length=32, verbose_name='车牌号')
    begintime = models.DateTimeField(auto_now=False, auto_now_add=False)
    carport = models.IntegerField(verbose_name='车位')

    # 设置表名称
    class Meta:
        db_table = "car_in_record"


# 离开车位
class Car_out_record(models.Model):
    carnum = models.CharField(max_length=32, verbose_name='车牌号')
    endtime = models.DateTimeField(auto_now=False, auto_now_add=False)
    carport = models.IntegerField(verbose_name='车位')

    # 设置表名称
    class Meta:
        db_table = "car_out_record"


# vip办卡收费
class Extra_charge(models.Model):
    carnum = models.CharField(max_length=32, verbose_name='车牌号')
    is_valid = models.BooleanField(default=False)
    vip_begintime = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    vip_deadline = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    money = models.IntegerField(verbose_name='收费')

    # 设置表名称
    class Meta:
        db_table = "extra_charge"

# python manage.py makemigrations
# python manage.py migrate
#使用这个命令可以生成数据库