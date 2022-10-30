from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from loguru import logger

from gateway.auth import do_auth
from gateway.users.models import User


router = APIRouter()

# TODO: move to external configuration
redirect_config = {
    'tasks': 'taskman:8080/tasks',
    'accounts': 'accounting:8080/accounts',
    'analytics': 'analytics:8080/analytics',
}


def get_redirector(r: Request) -> httpx.AsyncClient:
    return r.app.state.proxy_client


@router.get('/test')
async def test(r: Request):
    logger.warning('Got headers: {}', r.headers)
    return Response(status_code=200)


@router.api_route('/{resource}', methods=['GET', 'POST'], include_in_schema=False)
@router.api_route('/{resource}/{path:path}', methods=['GET', 'POST'], include_in_schema=False)
async def proxy_request(
    request: Request,
    resource: str,
    path: Optional[str] = None,
    auth_user: User = Depends(do_auth),
    client: httpx.AsyncClient = Depends(get_redirector),
) -> Response:
    proxy_path = make_proxy_path(resource, path)
    try:
        proxy_response = await client.request(
            method=request.method,
            url=httpx.URL(proxy_path),
            params=request.query_params,
            content=await request.body(),
            headers={'user_public_id': auth_user.public_id, 'user_role': auth_user.role},
        )
        return Response(
            status_code=proxy_response.status_code,
            content=proxy_response.content,
            headers=proxy_response.headers,
        )

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail='Unexpected error during proxying')


def make_proxy_path(resource: str, path: Optional[str]) -> str:
    redirect_to = redirect_config.get(resource)
    if redirect_to is None:
        raise HTTPException(status_code=404, detail=f'Redirect for resource {resource} not found')

    resourse_path = '/' + path.lstrip('/').rstrip('/') if path else ''
    return f'http://{redirect_to}{resourse_path}'
