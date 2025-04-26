import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Tuple
import json

def fetch_weather_data(city_code: str) -> str:
    """
    获取中国天气网指定城市7天天气预报和生活指数

    Args:
        city_code (str): 中国天气网城市编码，例如北京为101010100
        获取城市编码: https://j.i8tq.com/weather2020/search/city.js

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
            第一个DataFrame包含天气预报数据，列名为["日期", "天气状况", "温度", "风力"]
            第二个DataFrame包含生活指数数据，列名为["指数名称", "建议"]
    """
    # 请求头配置
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    BASE_URL = f"http://www.weather.com.cn/weather/{city_code}.shtml"

    try:
        # 发送HTTP请求
        response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        # 解析天气预报数据
        def parse_weather():
            weather_data = []
            for item in soup.select("ul.t.clearfix > li"):
                # 中文字段转英文标识
                date = item.select_one("h1").get_text(strip=True)
                condition = item.select_one("p.wea").get_text(strip=True)
                temp = item.select_one("p.tem").get_text(strip=True).replace("\n", "")
                wind_tag = item.select_one("p.win i")
                wind = wind_tag.get_text(strip=True) if wind_tag else ""

                weather_data.append({
                    "date": date,
                    "condition": condition,
                    "temperature": temp,
                    "wind": wind
                })
            return pd.DataFrame(weather_data)

        # 解析生活指数数据
        def parse_life_index():
            life_index_data = []
            livezs_div = soup.find("div", id="livezs")
            if livezs_div:
                for item in livezs_div.select("div.hide.show ul.clearfix > li"):
                    # 双重校验元素存在性
                    name_tag = item.select_one("em")
                    desc_tag = item.select_one("p")
                    if name_tag and desc_tag:
                        life_index_data.append({
                            "index_name": name_tag.get_text(strip=True),
                            "advice": desc_tag.get_text(strip=True)
                        })
                return pd.DataFrame(life_index_data)
            return None

        return json.dumps({
            "weather": parse_weather().to_dict(orient='records'),
            "life_index": parse_life_index().to_dict(orient='records')
        }, ensure_ascii=False)

    except Exception as e:
        error_msg = json.dumps({
            "error": f"Fetch Error (city:{city_code})",
            "detail": str(e)
        }, ensure_ascii=False)
        print(error_msg)
        return error_msg


# 示例用法
if __name__ == "__main__":
    result = fetch_weather_data("101190113")  # 北京
    print(result)