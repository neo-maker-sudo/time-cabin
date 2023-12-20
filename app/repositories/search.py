import requests
from abc import ABCMeta, abstractmethod
from fastapi import status
from app.config import setting
from app.enums.general import SearchServiceActionEnums
from app.exceptions.search import (
    RequestsTimeoutException,
    RequestsHttpErrorException,
    RequestsInvalidException,
)

class AbstractSearchRepository(object, metaclass=ABCMeta):

    @abstractmethod
    def search(self):
        raise NotImplemented

    @abstractmethod
    def get(self):
        raise NotImplemented


class YoutubeSearchRepository(AbstractSearchRepository):
    search_url: str = setting.YOUTUBE_SEARCH_URL
    get_video_url: str = setting.YOUTUBE_GET_VIDEO_URL
    search_params = {
        "q": None,
        "part": "snippet",
        "key": setting.YOUTUBE_API_KEY,
        "type": "videos",
        "maxResults": 20,
        "order": "date",
    }
    get_video_params = {
        "id": None,
        "key": setting.YOUTUBE_API_KEY,
        "part": "snippet",
    }

    def handling_response(self, response: requests.Response):
        # sample error message
        # {
        #     'error': {
        #         'code': 400,
        #         'message': 'API key not valid. Please pass a valid API key.',
        #         'errors': [
        #             {
        #                 'message': 'API key not valid. Please pass a valid API key.',
        #                 'domain': 'global',
        #                 'reason': 'badRequest'
        #             }
        #         ],
        #         'status': 'INVALID_ARGUMENT',
        #         'details': [
        #             {
        #                 '@type': 'type.googleapis.com/google.rpc.ErrorInfo',
        #                 'reason': 'API_KEY_INVALID',
        #                 'domain': 'googleapis.com',
        #                 'metadata': {
        #                     'service': 'youtube.googleapis.com'
        #                 }
        #             }
        #         ]
        #     }
        # }
        match response.status_code:
            case status.HTTP_200_OK:
                return response.json()

            case status.HTTP_400_BAD_REQUEST:
                raise RequestsInvalidException

            case _:
                raise RequestsHttpErrorException

    def update_params(self, params: dict, /, *, action: str) -> None:
        match action:
            case SearchServiceActionEnums.SEARCH:
                self.search_params.update(params)

            case SearchServiceActionEnums.GET:
                self.get_video_params.update(params)

            case _:
                pass

    def search(self, q: str, page_token: str):
        self.update_params(
            {
                "q": q,
                "pageToken": page_token
            },
            action=SearchServiceActionEnums.SEARCH
        )

        try:
            # https://developers.google.com/youtube/v3/guides/implementation/pagination?hl=zh-tw
            # https://developers.google.com/youtube/v3/docs/search/list?hl=zh-tw
            response = requests.get(
                self.search_url, params=self.search_params
            )

        except requests.exceptions.Timeout:
            raise RequestsTimeoutException

        except requests.exceptions.HTTPError:
            raise RequestsHttpErrorException

        return self.handling_response(response=response)

    def get(self, video_id: str):
        self.update_params({"id": video_id}, action=SearchServiceActionEnums.GET)

        try:
            response = requests.get(
                self.get_video_url, params=self.get_video_params
            )

        except requests.exceptions.Timeout:
            raise RequestsTimeoutException

        except requests.exceptions.HTTPError:
            raise RequestsHttpErrorException

        return self.handling_response(response=response)
