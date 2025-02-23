#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2022 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Display basic system information.

Needs psutil (+ dependencies) installed::

  $ sudo apt-get install python-dev
  $ sudo -H pip install psutil
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from datetime import datetime

if os.name != 'posix':
    sys.exit(f'{os.name} platform is not supported')

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont

try:
    import psutil
except ImportError:
    print("The psutil library was not found. Run 'sudo -H pip install psutil' to install it.")
    sys.exit()

# 全局變數
running = True
device = None  # 全局設備變數，用於清理

# 信號處理函數
def signal_handler(sig, frame):
    global running
    print("Received shutdown signal, exiting...")
    shutdown_display()
    running = False

# 清理顯示設備
def shutdown_display():
    global device
    if device is not None:
        try:
            with canvas(device) as draw:
                draw.rectangle(device.bounding_box, fill="black")  # 清空螢幕
            device.clear()  # 清空顯示內容
            device.hide()   # 隱藏顯示（若支援）
            print("Display cleared and shut down")
        except Exception as e:
            print(f"Error shutting down display: {e}")

def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return f"{n}B"

def cpu_usage():
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    av1, av2, av3 = os.getloadavg()
    return "Ld:%.1f %.1f %.1f Up: %s" \
        % (av1, av2, av3, str(uptime).split('.')[0])

def mem_usage():
    usage = psutil.virtual_memory()
    return "Mem: %s %.0f%%" \
        % (bytes2human(usage.used), 100 - usage.percent)

def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "SD:  %s %.0f%%" \
        % (bytes2human(usage.used), usage.percent)

def network(iface):
    stat = psutil.net_io_counters(pernic=True)[iface]
    return "%s: Tx%s, Rx%s" % \
           (iface, bytes2human(stat.bytes_sent), bytes2human(stat.bytes_recv))

def show_ip():
    """使用 hostname -I 獲取設備的 IP 地址"""
    try:
        ip_output = subprocess.check_output(['hostname', '-I'], text=True).strip()
        if ip_output:
            ip = ip_output.split()[0]
            return f"IP: {ip}"
        return "IP: Not connected"
    except subprocess.CalledProcessError:
        return "IP: Error retrieving IP"
    except Exception as e:
        return f"IP: Error ({str(e)})"

def stats(device):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 12)

    with canvas(device) as draw:
        draw.text((0, 0), cpu_usage(), font=font2, fill="white")
        if device.height >= 32:
            draw.text((0, 14), mem_usage(), font=font2, fill="white")

        if device.height >= 64:
            draw.text((0, 26), disk_usage('/'), font=font2, fill="white")
            try:
                draw.text((0, 38), network('wlan0'), font=font2, fill="white")
                draw.text((0, 50), show_ip(), font=font2, fill="white")
            except KeyError:
                # no wifi enabled/available
                pass

def main():
    global running, device
    device = get_device()  # 初始化設備

    # 檢查命令列參數
    if len(sys.argv) > 1 and sys.argv[1] == "--shutdown":
        shutdown_display()
        sys.exit(0)

    # 註冊信號處理
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    while running:
        try:
            stats(device)
            time.sleep(5)
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program terminated by user")
        shutdown_display()
    except Exception as e:
        print(f"Unexpected error: {e}")
        shutdown_display()
    finally:
        print("Service stopped")
