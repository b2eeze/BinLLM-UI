```c
void FUN_00100a80(void)
{
    char c = ' ';
    if (!FUN_00101023())
        c = '\x02';
    else
        __isoc99_fscanf(stdin, "%c", &c);
    if (!FUN_00101023()) {
        if (c == '\x7f')
            FUN_00100b7e("data value is too large to perform arithmetic safely.");
        else
            FUN_00100cb5(c + 1);
    } else
        FUN_00100cb5(c + 1);
}
```

