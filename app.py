# @falcon.ny
import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from config import Conf


app = Starlette(debug=True)


@app.route("/github_webhook")
class WebHook(HTTPEndpoint):
    '''

    :var result: <list> of <dict> [{`track title` : `artist name`}]
    '''

    async def get(self, request):
        resp = {'ok': True}
        return JSONResponse(resp)

    async def post(self, request):
        form = await request.form()
        return JSONResponse({'form': form})


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=50001)
