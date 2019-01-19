# @falcon.ny
import os
import json
import uvicorn
from uvicorn.main import run, get_logger
from uvicorn.reloaders.statreload import StatReload
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
        resp = {'ok': True, 'message': 'you got this'}
        return JSONResponse(resp)

    async def post(self, request):
        '''
        :var repo_id: <int>
        '''
        self.event = request.headers['X-GitHub-Event']
        form = await request.form()
        print(form)
        payload = json.loads(form['payload'])
        repo_id = payload['repository']['id']
        _sh = Conf.projects[repo_id]['shell_script']
        _dir = Conf.projects[repo_id]['dir']
        result = False

        if self.event == 'push':
            try:
                os.chdir(_dir)
                os.system('git pull')
                message = 'pulled from github.'
                if _sh:
                    result = not os.system(f'bash {_sh}')
                    if result:
                        message = f'successfully run {_sh}'
                    else:
                        message = f'failed run {_sh}'
            except Exception as e:
                message = e
        else:
            message = await self.echo(payload)
        resp = {'done': result, 'message': message}
        return JSONResponse(resp)

    async def echo(self, payload):
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
