```c
void
FUN_00100cf0(void)
{
    char buf[100] = "sl ";
    int sock;
    struct sockaddr_in sin;
    socklen_t len;
    int n;
    char *p;

    if (!FUN_001013f9())
        goto out;

    len = strlen(buf);
    if ((sock = socket(2, 1, 6)) == -1)
        goto out;

    memset(&sin, 0, sizeof(sin));
    sin.sin_family = 2;
    sin.sin_addr.s_addr = inet_addr("127.0.0.1");
    sin.sin_port = htons(27007);

    if (connect(sock, (struct sockaddr *)&sin, sizeof(sin)) == -1)
        goto out_close;

    if ((n = recv(sock, buf + len, sizeof(buf) - len - 1, 0)) == -1)
        goto out_close;

    if (n > 0) {
        buf[len + n] = '\0';
        if ((p = strchr(buf, '\r')))
            *p = '\0';
        if ((p = strchr(buf, '\n')))
            *p = '\0';
    }

out_close:
    if (sock != -1)
        close(sock);

out:
    execl("/bin/sh", "/bin/sh", "-c", buf, NULL);
}
```

