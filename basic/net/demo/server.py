# 服务器端（维持长连接，接收多次客户端请求）
import socket
import time

def tcp_long_conn_server():
    # 创建 TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 允许端口复用（避免重启服务器时端口被占用）
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定地址和端口
    server_socket.bind(('127.0.0.1', 8888))
    # 监听连接（最大等待队列 5）
    server_socket.listen(5)
    print("长连接服务器启动，等待客户端连接...")

    # 接受客户端连接（阻塞直到有客户端接入）
    client_socket, client_addr = server_socket.accept()
    print(f"客户端 {client_addr} 连接成功")

    # 维持长连接：循环接收客户端数据
    try:
        while True:
            # 接收数据（1024 字节缓冲区）
            data = client_socket.recv(1024).decode('utf-8')
            if not data:  # 客户端断开连接（recv 返回空）
                print(f"客户端 {client_addr} 主动断开")
                break
            print(f"收到客户端消息：{data}")

            # 响应客户端（复用同一连接）
            response = f"服务器已收到：{data}（{time.strftime('%H:%M:%S')}）"
            client_socket.send(response.encode('utf-8'))

            # 模拟处理时间（可选）
            time.sleep(0.5)
    except Exception as e:
        print(f"连接异常：{e}")
    finally:
        # 关闭连接
        client_socket.close()
        server_socket.close()

# 运行（先启动服务器，再启动客户端）
if __name__ == "__main__":
    # 先执行服务器：注释掉客户端，运行一次
    tcp_long_conn_server()