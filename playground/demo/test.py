def get_app_secret():
    # 定义密钥的字符数组
    chars = [
        'L', 'r', 'M', 'b', 'u', '5', 'o', 'U', 'a', 'z',
        '1', 'L', 'Q', 'z', 'V', 'f', 'P', 'q', 'w', 'f',
        'b', '8', 'R', '2', '4', 'X', 'U', 'q', '3', 'g',
        'U',
    ]
    return ''.join(chars)

if __name__ == '__main__':
    print(get_app_secret())
