# @falcon.ny
import os
import json
import redis
import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from uvicorn.main import run
from uvicorn.reloaders.statreload import StatReload

from config import Conf


app = Starlette(debug=True)
cpool = redis.ConnectionPool(host='localhost',
                             port=6379,
                             decode_responses=True,
                             db=0)
r = redis.Redis(connection_pool=cpool)
reloader = StatReload()
reloader.run(run, {
    'app': app,
    'host': '0.0.0.0',
    'port': 50001,
    'debug': 'true'
})


@app.route("/github_webhook")
class WebHook(HTTPEndpoint):
    '''

    On `push` event, do a shell script which should be set in config.py

    '''
    repo_id = Conf.projects['gws']
    pid = os.getpid()
    print(f'repo_id: {repo_id}')
    print(f'pid: {pid}')
    r.set(repo_id, pid)
    print(r.get(repo_id))

    def __del__(self):
        r.delete(self.repo_id)

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
        pid = r.get(repo_id)
        print(pid)
        _sh = Conf.projects[repo_id]['shell_script']
        _dir = Conf.projects[repo_id]['dir']
        result = False

        if event == 'push':
            try:
                # normally `_sh` return `0`, which could be considered as False
                os.chdir(_dir)
                # always accept a `pid` param for killing the old one
                result = not os.system(f'bash {_sh} {pid}')
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
    uvicorn.run(app, host='0.0.0.0', port=50001)
