import asyncio
import time
from typing import Coroutine, Any


# -------------------------- 1. 定义回调函数（处理异步任务结果）--------------------------
def task_callback(future: asyncio.Future) -> None:
    """
    异步任务完成后的回调函数
    :param future: 异步任务对象，通过 future.result() 获取任务返回值
    """
    try:
        # 获取异步任务的执行结果
        task_result = future.result()
        print(f"\n📢 回调函数触发：任务执行成功！")
        print(f"任务 ID：{task_result['task_id']}")
        print(f"任务结果：{task_result['data']}")
        print(f"耗时：{task_result['cost_time']:.2f} 秒")

        # 此处可扩展实际业务逻辑：如保存结果到数据库、发送通知等
        # save_to_db(task_result)  # 示例：保存到数据库
        # send_notification(task_result)  # 示例：发送通知

    except Exception as e:
        # 捕获异步任务执行过程中的异常
        print(f"\n❌ 回调函数触发：任务执行失败！错误：{str(e)}")


# -------------------------- 2. 定义异步任务（模拟耗时操作）--------------------------
async def async_task(task_id: int, sleep_time: float) -> dict:
    """
    异步任务：模拟耗时操作（如 API 调用、文件下载）
    :param task_id: 任务 ID（用于区分不同任务）
    :param sleep_time: 模拟耗时时间（秒）
    :return: 任务执行结果（字典）
    """
    print(f"🚀 任务 {task_id} 启动，预计耗时 {sleep_time} 秒")
    start_time = time.time()

    # 模拟耗时操作（如网络请求、文件处理）
    await asyncio.sleep(sleep_time)

    # 模拟任务结果（实际场景可能是 API 返回数据、文件处理后的结果）
    end_time = time.time()
    cost_time = end_time - start_time
    return {
        "task_id": task_id,
        "data": f"任务 {task_id} 异步执行完成的结果数据",
        "cost_time": cost_time
    }


# -------------------------- 3. 定义异步主函数（管理任务和回调）--------------------------
async def main():
    print("=== 异步任务 + 回调函数 演示开始 ===")
    start_total_time = time.time()

    # 步骤1：创建3个异步任务（并发执行）
    tasks = [
        async_task(task_id=1, sleep_time=2),  # 任务1：耗时2秒
        async_task(task_id=2, sleep_time=1),  # 任务2：耗时1秒（最快完成）
        async_task(task_id=3, sleep_time=3)  # 任务3：耗时3秒（最慢完成）
    ]

    # 步骤2：为每个任务绑定回调函数（任务完成后自动触发）
    task_futures = []
    for coro in tasks:
        # 将协程包装为 Future 对象（可绑定回调）
        future = asyncio.create_task(coro)
        # 绑定回调函数：任务完成后调用 task_callback
        future.add_done_callback(task_callback)
        task_futures.append(future)

    # 步骤3：等待所有任务执行完成（并发执行，总耗时 ≈ 最长任务耗时3秒）
    await asyncio.gather(*task_futures)

    # 步骤4：所有任务完成后的汇总
    total_cost_time = time.time() - start_total_time
    print(f"\n=== 所有任务执行完毕！总耗时：{total_cost_time:.2f} 秒 ===")


# -------------------------- 4. 运行异步程序 --------------------------
if __name__ == "__main__":
    # Python 3.7+ 推荐用 asyncio.run() 运行异步主函数
    asyncio.run(main())