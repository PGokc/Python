import socket
import time

# 客户端（复用长连接，发送多次请求）
def tcp_long_conn_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接服务器（建立长连接）
    client_socket.connect(('127.0.0.1', 8888))
    print("连接服务器成功，开始发送消息...")

    try:
        # 复用连接发送 5 次请求
        for i in range(5):
            message = f"CSGO 玩家指令 {i + 1}：前进、射击"
            client_socket.send(message.encode('utf-8'))
            # 接收服务器响应
            response = client_socket.recv(1024).decode('utf-8')
            print(f"服务器响应：{response}")
            time.sleep(1)  # 每隔 1 秒发一次
    except Exception as e:
        print(f"客户端异常：{e}")
    finally:
        # 主动关闭连接
        client_socket.close()
        print("客户端断开连接")


# 运行（先启动服务器，再启动客户端）
if __name__ == "__main__":
    # 再执行客户端：注释掉服务器，运行一次
    tcp_long_conn_client()