from django.db import models
import filetype
from User.models import User
import hashlib
import zlib

# Create your models here.
class Firmwares(models.Model):
    local_url = models.CharField(max_length=255, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    size = models.IntegerField(blank=True, null=True)

    user = models.CharField(max_length=255, default='default')
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    hash_value = models.CharField(max_length=255, blank=True, null=True)
    taint_label = models.IntegerField(blank=True, null=True)
    call_chain = models.TextField(default="no call chain yet")
    checksec = models.TextField(default="checksec error")
    # 取消原先本地保存的策略
    md_path = models.CharField(max_length=255, blank=True)
    json_path = models.CharField(max_length=255, blank=True)
    dc_path = models.CharField(max_length=255, blank=True)

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')  # 自动设置当前的日期和时间。之后，这个字段的值不会再改变
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    delete_time = models.DateTimeField(null=True, blank=True, verbose_name='Delete time')

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_firmwares')

    def filesize(self):

        x = int(self.size)
        y = 512000
        if x < y:
            value = round(x / 1024, 2)
            ext = ' KB'
        elif x < y * 1024:
            value = round(x / (1024 * 1024), 2)
            ext = ' MB'
        else:
            value = round(x / (1024 * 1024 * 1024), 2)
            ext = ' GB'
        return str(value) + ext

    def filetype(self):
        file_type = filetype.guess(f"uploads_dataset/{self.file_name}")
        if file_type:
            return file_type.mime
        else:
            return "未知类型"

    def calculate_hash(self):

        # 初始化哈希对象
        md5_hasher = hashlib.md5()
        sha1_hasher = hashlib.sha1()
        sha256_hasher = hashlib.sha256()
        sha512_hasher = hashlib.sha512()
        crc32_value = 0

        file_path = f"uploads_dataset/{self.file_name}"
        with open(file_path, 'rb') as file:
            md5_hasher.update(file.read())
            sha1_hasher.update(file.read())
            sha256_hasher.update(file.read())
            sha512_hasher.update(file.read())
            crc32_value = zlib.crc32(file.read(), crc32_value)

        # 获取哈希值和 CRC32 值
        md5_hash = md5_hasher.hexdigest()
        sha1_hash = sha1_hasher.hexdigest()
        sha256_hash = sha256_hasher.hexdigest()
        sha512_hash = sha512_hasher.hexdigest()
        crc32_value = format(crc32_value & 0xFFFFFFFF, '08x')

        md_output = (
            f"#### Hashes for file:\n\n"
            f"- **MD5:** {md5_hash}\n"
            f"- **SHA1:** {sha1_hash}\n"
            f"- **SHA256:** {sha256_hash}\n"
            f"- **SHA512:** {sha512_hash}\n"
            f"- **CRC32:** {crc32_value}\n"
        )

        return md_output
