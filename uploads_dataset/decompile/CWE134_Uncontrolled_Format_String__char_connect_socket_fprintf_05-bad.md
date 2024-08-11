```c
void
FUN_00100d40(void)
{
    int sock;
    struct sockaddr_in addr;
    char buf[100] = {0};
    size_t len = strlen(buf);

    if (!DAT_00303010)
        return;

    sock = socket(2, 1, 6);
    if (sock == -1)
        goto out;

    memset(&addr, 0, sizeof(addr));
    addr.sin_family = 2;
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    addr.sin_port = htons(27007);

    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) == -1)
        goto out;

    {
        int n = recv(sock, buf + len, sizeof(buf) - len - 1, 0);
        if (n == -1 || n == 0)
            goto out;
        buf[len + n] = '\0';
    }

    {
        char *p = strchr(buf, '\r');
        if (p)
            *p = '\0';
    }

    {
        char *p = strchr(buf, '\n');
        if (p)
            *p = '\0';
    }

out:
    if (sock != -1)
        close(sock);

    if (DAT_00303010)
        fprintf(stdout, buf);
}
```

