import requests
import wikipedia
from utils import setup_logger

logger = setup_logger(__name__)
DEFAULT_TIMEOUT = 10


class WeatherService:
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.timeout = timeout

    def get(self, city: str) -> dict:
        try:
            r = requests.get(
                self.BASE_URL,
                params={"q": city, "appid": self.api_key, "units": "metric"},
                timeout=self.timeout,
            )
            data = r.json()
            if str(data.get("cod")) == "200":
                return {
                    "temp": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "city": city,
                }
            return {"error": data.get("message", "City not found")}
        except requests.Timeout:
            return {"error": "Weather request timed out"}
        except Exception :
            logger.error("Weather error")
            return {"error": "Unable to fetch weather"}


class NewsService:
    BASE_URL = "https://api.freenewsapi.io/v1/news"

    def __init__(
        self,
        api_key: str,
        country: str = "in",
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.country = country
        self.timeout = timeout

    def get_top(self, limit: int = 5):
        try:
            r = requests.get(
                self.BASE_URL,
                headers={
                    "x-api-key": self.api_key,
                },
                params={
                    "country": self.country,
                    "language": "en",
                },
                timeout=self.timeout,
            )

            r.raise_for_status()
            data = r.json()

            articles = data.get("data", [])

            if articles:
                return [
                    article.get("title", "Untitled")
                    for article in articles[:limit]
                ]

            return {"error": "No news articles found"}

        except requests.Timeout:
            return {"error": "News request timed out"}

        except requests.HTTPError as e:
            logger.error("News HTTP error")

            if e.response is not None and e.response.status_code == 401:
                return {"error": "Invalid News API key"}

            return {"error": "News service request failed"}

        except requests.RequestException:
            logger.error("News request error")
            return {"error": "Unable to connect to news service"}

        except Exception:
            logger.error("News error")
            return {"error": "Unable to fetch news"}


class WikiService:
    @staticmethod
    def search(query: str, sentences: int = 3):
        try:
            return wikipedia.summary(query, sentences=sentences)
        except wikipedia.exceptions.DisambiguationError as e:
            return {"disambiguation": e.options[:5]}
        except wikipedia.exceptions.PageError:
            return {"error": "Page not found"}
        except Exception as e:
            logger.error("Wiki error: %s", e)
            return {"error": "Wikipedia unavailable"}