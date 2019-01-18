# @falcon.ny
import os
import json
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

    async def get(self, request):
        resp = {'ok': True}
        return JSONResponse(resp)

    async def post(self, request):
        '''

        :var repo_id: <int> here we should pay attn. on this exception
        '''
        event = request.headers['X-GitHub-Event']
        form = await request.form()
        payload = json.loads(form['payload'])
        repo_id = payload['repository']['id']
        _sh = Conf.projects[repo_id]['shell_script']
        _dir = Conf.projects[repo_id]['dir']
        result = False

        if event == 'push':
            try:
                # normally `_sh` return `0`, which could be considered as False
                os.chdir(_dir)
                result = not os.system(f'bash {_sh}')
                if result:
                    message = f'successfully run {_sh}'
                else:
                    message = f'failed run {_sh}'
            except Exception as e:
                message = e
        else:
            message = f'only deal with push event, got {event}'
        resp = {'done': result, 'message': message}
        return JSONResponse(resp)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=50001)
