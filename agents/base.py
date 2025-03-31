from abc import ABC, abstractmethod

class WeatherAgent(ABC):
    """
    すべての天気予報エージェントが継承すべき抽象クラス。
    """

    @abstractmethod
    def fetch(self, location: dict) -> dict:
        """
        天気予報データを取得して返す。

        Args:
            location (dict): 地点情報。例：
                {
                    "name": "千葉市",
                    "lat": 35.6,
                    "lon": 140.1,
                    "code": "120010"  # 任意：必要なAPIが使う場合のみ
                }

        Returns:
            dict: 正規化された天気データ。例：
                {
                    "source": "OpenWeatherMap",
                    "max_temp": 26.4,
                    "min_temp": 18.2,
                    "pop": 40,  # 降水確率（％）
                    "description": "optional"
                }
        """
        pass
