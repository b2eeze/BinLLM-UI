import markdown
import hashlib
import requests
import json
import os
import re
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.utils.timezone import now
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.http import FileResponse

from .models import Firmwares
from User.models import User

url = "https://widely-fitting-lacewing.ngrok-free.app/upload"

# Create your views here.


def index(request):

    return render(request, "index.html")


def about(request):

    return render(request, "index.html")


def upload_file(request):
    user = request.user
    # print(user.is_anonymous)
    print(user.is_authenticated)
    if not user.is_authenticated:
        return redirect("User:login")
    return render(request, "upload_file.html")

def upload_multi_file(request):
    user = request.user

    if not user.is_authenticated:
        return redirect("User:login")

    return render(request, "upload_multi_file.html")



@csrf_exempt
def process_file(request):
    user = request.user
    if not user.is_authenticated:
        redirect("User:login")
    if request.method == "POST":
        file = request.FILES.getlist('file_data')[0]

        file_hash = hashlib.md5(file.read()).hexdigest()
        file.seek(0)  # 重置文件指针位置

        # 检查是否存在相同内容的文件
        existing_files = default_storage.listdir('uploads_dataset')[1]
        file_exists = False
        file_url = ""
        for existing_file in existing_files:
            existing_file_path = os.path.join('uploads_dataset', existing_file)
            with default_storage.open(existing_file_path, 'rb') as f:
                existing_file_hash = hashlib.md5(f.read()).hexdigest()
                if file_hash == existing_file_hash:
                    file_url = existing_file_path
                    file_exists = True

        if not file_exists:
            print("save new")
            # 将文件保存到本地文件夹
            path = default_storage.save(f'uploads_dataset/{file.name}', ContentFile(file.read()))
            file_url = default_storage.url(path)

        if not Firmwares.objects.filter(hash_value=file_hash).exists():
            # 上传文件到远程服务器处理，利用 requests 库实现
            files = {'file': file}
            response = requests.post(url, files=files)
            json_data = response.json()

            # markdown 文件
            md_con = json_data['markdown']
            flag_line = md_con.splitlines()[-1]
            pattern = r"存在CWE-\d+漏洞"
            if re.search(pattern, flag_line):
                tl = 1
            else:
                tl = 0
            with open(f'uploads_dataset/markdown/{file.name}.md', 'w', encoding='utf-8') as f:
                f.write(md_con)

            # 反汇编 json 文件
            dc_con = json_data['decompile']
            if "{" not in dc_con:
                dc_json = "{ }"
            else:
                dc_json = json.loads(dc_con)

            with open(f'uploads_dataset/json/{file.name}.json', 'w', encoding='utf-8') as f:
                f.write(dc_json)

            # 函数调用链
            cc = json_data["call_chain"]
            # 反汇编代码
            ef = json_data["extract_func"]
            rf = json_data["refined_func"]

            decompile_code = ""
            decompile_code += "#### extract_func\n\n" + "```c\n" + ef + "\n" + "```\n\n"
            decompile_code += "#### refined_func\n\n" + "```c\n" + rf + "\n" + "```\n\n"
            with open(f'uploads_dataset/decompile/{file.name}.md', 'w', encoding='utf-8') as f:
                f.write(decompile_code)

            stdout = json_data['stdout']
            lines = stdout.strip().split('\n')
            headers = re.split(r'\s{2,}|\t', lines[0])
            values = re.split(r'\s{2,}|\t', lines[1])

            ansi_escape = re.compile(r'\x1b\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]')
            # 移除 ANSI 转义序列
            clean_values = [ansi_escape.sub('', value) for value in values]
            clean_values = list(filter(None, clean_values))

            # print(headers)
            # print(clean_values)

            # # 构建 Markdown 列表
            # markdown_list = []
            # for header, value in zip(headers, clean_values):
            #     markdown_list.append(f"- **{header}:** {value}")
            #
            # # 将列表拼接为一个字符串，并打印输出
            # markdown_output = '\n'.join(markdown_list)
            # print("checksec.....")
            # print(stdout)
            # print(markdown_output)

            table_header = "| property | value |\n"
            table_header += "|----------|----------|\n"

            # 创建表格内容
            table_rows = []
            for header, value in zip(headers, clean_values):
                table_rows.append(f"| **{header}** | {value} |")

            # 组合表头和表格内容
            markdown_table = table_header + "\n".join(table_rows)

            print(markdown_table)

            # 保存新的数据到数据库
            firmware = Firmwares(
                local_url=file_url,
                file_name=file.name,
                size=file.size,
                user="",
                hash_value=file_hash,
                taint_label=tl,
                call_chain=cc,
                md_path=f'uploads_dataset/markdown/{file.name}.md',
                dc_path=f'uploads_dataset/decompile/{file.name}.md',
                json_path=f'uploads_dataset/json/{file.name}.json',
                checksec=markdown_table,
                creator=user,
            )
            firmware.save()

        else:
            print("existing")

        return JsonResponse({'file_hash': file_hash, "file_exist": file_exists})


@csrf_exempt
def process_multi_file(request):
    user = request.user
    if not user.is_authenticated:
        redirect("User:login")

    # 来自前端 js 的文件
    if request.method == "POST":
        files = request.FILES.getlist('file_data')

        # 返回给前端显示的表格数据
        file_json_list = []

        for file in files:
            # 表格的一行数据
            file_json = {
                "hash": None,
                "file_name": None,
                "create_time": None,
                "file_type": None,
                "file_size": None,
            }

            # 计算文件哈希值
            file_hash = hashlib.md5(file.read()).hexdigest()
            file.seek(0)  # 重置文件指针位置

            # 准备表格数据 第一部分
            file_json['hash'] = file_hash
            file_json['file_name'] = file.name[:10]

            # 检查本地文件夹是否存在相同内容的文件
            existing_files = default_storage.listdir('uploads_dataset')[1]
            file_exists = False

            file_url = ""
            for existing_file in existing_files:
                existing_file_path = os.path.join('uploads_dataset', existing_file)
                with default_storage.open(existing_file_path, 'rb') as f:
                    existing_file_hash = hashlib.md5(f.read()).hexdigest()
                    # 存在
                    if file_hash == existing_file_hash:
                        file_url = existing_file_path
                        file_exists = True
                        break
            # 不存在
            if not file_exists:
                print("save new")
                # 将文件保存到本地文件夹
                path = default_storage.save(f'uploads_dataset/{file.name}', ContentFile(file.read()))
                file_url = default_storage.url(path)
            # 检查结束

            # 检查数据库中是否有相关文件记录
            if not Firmwares.objects.filter(hash_value=file_hash).exists():
                # 上传文件到远程服务器处理，利用 requests 库实现
                files = {'file': file}
                response = requests.post(url, files=files)
                json_data = response.json()

                # markdown 文件
                md_con = json_data['markdown']
                flag_line = md_con.splitlines()[-1]
                pattern = r"存在CWE-\d+漏洞"
                if re.search(pattern, flag_line):
                    tl = 1
                else:
                    tl = 0
                with open(f'uploads_dataset/markdown/{file.name}.md', 'w', encoding='utf-8') as f:
                    f.write(md_con)

                # 反汇编 json 文件
                dc_con = json_data['decompile']
                if "{" not in dc_con:
                    dc_json = "{ }"
                else:
                    dc_json = json.loads(dc_con)

                with open(f'uploads_dataset/json/{file.name}.json', 'w', encoding='utf-8') as f:
                    f.write(dc_json)

                # 函数调用链
                cc = json_data["call_chain"]
                # 反汇编代码
                ef = json_data["extract_func"]
                rf = json_data["refined_func"]

                decompile_code = ""
                decompile_code += "#### extract_func\n\n" + "```c\n" + ef + "\n" + "```\n\n"
                decompile_code += "#### refined_func\n\n" + "```c\n" + rf + "\n" + "```\n\n"
                with open(f'uploads_dataset/decompile/{file.name}.md', 'w', encoding='utf-8') as f:
                    f.write(decompile_code)

                stdout = json_data['stdout']
                lines = stdout.strip().split('\n')
                headers = re.split(r'\s{2,}|\t', lines[0])
                values = re.split(r'\s{2,}|\t', lines[1])

                ansi_escape = re.compile(r'\x1b\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]')
                # 移除 ANSI 转义序列
                clean_values = [ansi_escape.sub('', value) for value in values]
                clean_values = list(filter(None, clean_values))

                # print(headers)
                # print(clean_values)

                # 构建 Markdown 列表
                # markdown_list = []
                # for header, value in zip(headers, clean_values):
                #     markdown_list.append(f"- **{header}:** {value}")
                #
                # # 将列表拼接为一个字符串，并打印输出
                # markdown_output = '\n'.join(markdown_list)
                # print(markdown_output)

                table_header = "| property | value |\n"
                table_header += "|----------|----------|\n"

                # 创建表格内容
                table_rows = []
                for header, value in zip(headers, clean_values):
                    table_rows.append(f"| **{header}** | {value} |")

                # 组合表头和表格内容
                markdown_table = table_header + "\n".join(table_rows)

                print(markdown_table)

                # 保存新的数据到数据库
                firmware = Firmwares(
                    local_url=file_url,
                    file_name=file.name,
                    size=file.size,
                    user="",
                    hash_value=file_hash,
                    taint_label=tl,
                    call_chain=cc,
                    md_path=f'uploads_dataset/markdown/{file.name}.md',
                    dc_path=f'uploads_dataset/decompile/{file.name}.md',
                    json_path=f'uploads_dataset/json/{file.name}.json',
                    checksec=markdown_table,
                    creator=user,
                )
                firmware.save()
            # 检查结束
            else:
                firmware = Firmwares.objects.filter(hash_value=file_hash)[0]

            # 准备表格数据 第二部分
            file_json['create_time'] = firmware.create_time.strftime('%Y-%m-%d')
            file_json['file_type'] = firmware.filetype()
            file_json['file_size'] = firmware.filesize()

            file_json_list.append(file_json)

        # 表格的表头
        keys = ["file_name","create_time","file_type","file_size"]
        return JsonResponse({'file_json_list': file_json_list, 'keys': keys})

    return render(request, "upload_multi_file.html")


def history(request):
    items = Firmwares.objects.all()
    labels = ['存在漏洞', '无漏洞']
    data_clean = 0
    data_taint = 0
    for item in items:
        if item.taint_label == 1:
            data_taint += 1
        else:
            data_clean += 1
    data = [data_clean, data_taint]
    chart_data = {"labels": labels, "data": data}

    today = datetime.now()
    labels = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    # 初始化结果字典
    dist = {label: 0 for label in labels}
    # 遍历数据库中的数据并填充结果
    for item in items:
        date_str = item.create_time.strftime('%Y-%m-%d')
        if date_str in dist:
            dist[date_str] += 1

    dist = dict(sorted(dist.items()))
    labels = list(dist.keys())
    data = list(dist.values())

    bar_data = {"labels": labels, "data": data}
    print(bar_data)

    return render(request, "tables.html", {"items": items, "chart_data": chart_data, "bar_data": bar_data})


def detailed_file(request, hash_id):
    print("hash id", hash_id)
    print(type(request))
    match = Firmwares.objects.filter(hash_value=hash_id)[0]

    md = open(match.md_path, 'r', encoding='utf-8').read()
    js = json.load(open(match.json_path, 'r', encoding='utf-8'))
    dc = open(match.dc_path, 'r', encoding='utf-8').read()
    # 从数据库中读取
    md_repo = markdown.markdown(md, extensions=[
                 'markdown.extensions.extra',
                 'markdown.extensions.codehilite',
                 'markdown.extensions.toc',
              ])
    dc_repo = markdown.markdown(dc, extensions=[
                 'markdown.extensions.extra',
                 'markdown.extensions.codehilite',
                 'markdown.extensions.toc',
              ])
    cs = markdown.markdown(match.checksec, extensions=[
                 'markdown.extensions.extra',
                 'markdown.extensions.codehilite',
                 'markdown.extensions.toc',
              ])
    hs = markdown.markdown(match.calculate_hash(), extensions=[
                 'markdown.extensions.extra',
                 'markdown.extensions.codehilite',
                 'markdown.extensions.toc',
              ])
    return render(request, "detailed_file.html",
                  {"match": match, "md_repo": md_repo, "dc_repo": dc_repo, "js": js,
                   "cs": cs, "hs": hs})



def file_delete(request, hash_id):
    print("hash id", hash_id)
    print(type(request))

    Firmwares.objects.filter(hash_value=hash_id).delete()

    return redirect("BinLLM:history")


def file_download(request, hash_id):
    file_obj = Firmwares.objects.get(hash_value=hash_id)
    repo_file_path = file_obj.md_path
    repo_file_name = file_obj.file_name
    if os.path.exists(repo_file_path):
        response = FileResponse(open(repo_file_path, 'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}.md".format(repo_file_name)
        return response
    else:
        return redirect("BinLLM:history")


def file_rehandle(request, hash_id):
    user = request.user
    if request.method == "POST":
        file_obj = Firmwares.objects.get(hash_value=hash_id)
        file_path = os.path.join('uploads_dataset', file_obj.file_name)
        with default_storage.open(file_path, 'rb') as file:
            # 上传文件到远程服务器处理，利用 requests 库实现
            files = {'file': file}
            response = requests.post(url, files=files)
            json_data = response.json()

            # markdown 文件
            md_con = json_data['markdown']
            flag_line = md_con.splitlines()[-1]
            pattern = r"存在CWE-\d+漏洞"
            if re.search(pattern, flag_line):
                tl = 1
            else:
                tl = 0
            with open(f'uploads_dataset/markdown/{file.name}.md', 'w', encoding='utf-8') as f:
                f.write(md_con)

            # 反汇编 json 文件
            dc_con = json_data['decompile']
            if "{" not in dc_con:
                dc_json = "{ }"
            else:
                dc_json = json.loads(dc_con)

            with open(f'uploads_dataset/json/{file.name}.json', 'w', encoding='utf-8') as f:
                f.write(dc_json)

            # 函数调用链
            cc = json_data["call_chain"]
            # 反汇编代码
            ef = json_data["extract_func"]
            rf = json_data["refined_func"]

            decompile_code = ""
            decompile_code += "#### extract_func\n\n" + "```c\n" + ef + "\n" + "```\n\n"
            decompile_code += "#### refined_func\n\n" + "```c\n" + rf + "\n" + "```\n\n"
            with open(f'uploads_dataset/decompile/{file.name}.md', 'w', encoding='utf-8') as f:
                f.write(decompile_code)
            file_obj.taint_label=tl
            file_obj.save()


    return redirect("BinLLM:detailed_file", hash_id)
