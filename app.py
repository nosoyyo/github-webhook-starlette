# @falcon.ny
import os
import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from config import Conf


app = Starlette(debug=True)


@app.route("/github_webhook")
class WebHook(HTTPEndpoint):
    '''

    On `push` event, do a shell script which should be set in config.py

    '''

    _sh = Conf._sh

    async def get(self, request):
        resp = {'ok': True}
        return JSONResponse(resp)

    async def post(self, request):
        event = request.headers['X-GitHub-Event']
        result = False
        if event == 'push':
            # normally `_sh` return `0`, which could be considered as False
            result = not os.system(f'bash {self._sh}')
            if result:
                message = f'successfully run {self._sh}'
            else:
                message = f'failed run {self._sh}'
        else:
            message = f'only deal with push event, got {event}'
        resp = {'result': result, 'message': message}
        return JSONResponse(resp)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=50001)
