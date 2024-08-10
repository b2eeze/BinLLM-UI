#### extract_func

```c
 
void FUN_00100cf0(void)

{
  int __fd;
  int iVar1;
  size_t sVar2;
  ssize_t sVar3;
  char *pcVar4;
  long lVar5;
  undefined8 *puVar6;
  long in_FS_OFFSET;
  sockaddr local_88;
  undefined8 local_78;
  undefined8 local_70 [12];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  local_78 = 0x20736c;
  puVar6 = local_70;
  for (lVar5 = 0xb; lVar5 != 0; lVar5 = lVar5 + -1) {
    *puVar6 = 0;
    puVar6 = puVar6 + 1;
  }
  *(undefined4 *)puVar6 = 0;
  sVar2 = strlen((char *)&local_78);
  __fd = socket(2,1,6);
  if (__fd != -1) {
    memset(&local_88,0,0x10);
    local_88.sa_family = 2;
    local_88.sa_data._2_4_ = inet_addr("127.0.0.1");
    local_88.sa_data._0_2_ = htons(0x6987);
    iVar1 = connect(__fd,&local_88,0x10);
    if (iVar1 != -1) {
      sVar3 = recv(__fd,(char *)((long)&local_78 + sVar2),99 - sVar2,0);
      iVar1 = (int)sVar3;
      if ((iVar1 != -1) && (iVar1 != 0)) {
        *(char *)((long)&local_78 + (long)iVar1 + sVar2) = '\0';
        pcVar4 = strchr((char *)&local_78,0xd);
        if (pcVar4 != (char *)0x0) {
          *pcVar4 = '\0';
        }
        pcVar4 = strchr((char *)&local_78,10);
        if (pcVar4 != (char *)0x0) {
          *pcVar4 = '\0';
        }
      }
    }
  }
  if (__fd != -1) {
    close(__fd);
  }
  execl("/bin/sh","/bin/sh",&DAT_0010152e,&local_78,0);
  if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


```

#### refined_func

```c
void
FUN_00100cf0(void)
{
    char buf[100] = "sl";
    char *p;
    int sock;
    struct sockaddr_in sin;
    int len;

    len = strlen(buf);
    if ((sock = socket(2, 1, 6)) == -1)
        goto out;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = 2;
    sin.sin_addr.s_addr = inet_addr("127.0.0.1");
    sin.sin_port = htons(27007);
    if (connect(sock, (struct sockaddr *)&sin, sizeof(sin)) == -1)
        goto out;
    if ((len = recv(sock, buf + len, sizeof(buf) - len - 1, 0)) == -1)
        goto out;
    if (len) {
        buf[len + len] = '\0';
        if ((p = strchr(buf, '\r')))
            *p = '\0';
        if ((p = strchr(buf, '\n')))
            *p = '\0';
    }
out:
    if (sock != -1)
        close(sock);
    execl("/bin/sh", "/bin/sh", "-c", buf, NULL);
}
```

