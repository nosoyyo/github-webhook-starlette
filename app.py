# @falcon.ny
import os
import json
import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from uvicorn.main import run, get_logger
from uvicorn.reloaders.statreload import StatReload

from config import Conf


app = Starlette(debug=True)


@app.route("/github_webhook")
class WebHook(HTTPEndpoint):
    '''

    On `push` event, do a shell script which should be set in config.py

    '''
    repo_id = Conf.projects['gws']

    async def get(self, request):
        resp = {'ok': True, 'message': 'you got this'}
        return JSONResponse(resp)

    async def post(self, request):
        '''
        :var repo_id: <int> here we should pay attn. on this exception
        '''
        event = request.headers['X-GitHub-Event']
        self.event = event
        form = await request.form()
        print(form)
        payload = json.loads(form['payload'])
        repo_id = payload['repository']['id']
        _sh = Conf.projects[repo_id]['shell_script']
        _dir = Conf.projects[repo_id]['dir']
        result = False

        if event == 'push':
            try:
                # normally `_sh` return `0`, which could be considered as False
                os.chdir(_dir)
                # always accept a `pid` param for killing the old one
                result = not os.system(f'bash {_sh}')
                if result:
                    message = f'successfully run {_sh}'
                else:
                    message = f'failed run {_sh}'
            except Exception as e:
                message = e
        else:
            message = await self.getPingMessage(payload)
        resp = {'done': result, 'message': message}
        return JSONResponse(resp)

    async def getPingMessage(self, payload):
        return f"got `{self.event}` from {payload['repository']['full_name']}"


if __name__ == '__main__':
    reloader = StatReload(get_logger('debug'))
    reloader.run(run, {
        'app': app,
        'host': '0.0.0.0',
        'port': 50001,
        'log_level': 'debug',
        'debug': 'true'
    })
    uvicorn.run(app=app,
                host='0.0.0.0',
                port=50001,
                log_level='debug',
                debug='true')
