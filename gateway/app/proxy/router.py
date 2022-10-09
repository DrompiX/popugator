from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from loguru import logger

from auth import do_auth
from users.models import User


router = APIRouter()

# TODO: move to external configuration
redirect_config = {
    'tasks': 'localhost:8080/test',
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
    redirect_to = redirect_config.get(resource)
    if redirect_to is None:
        raise HTTPException(status_code=404, detail=f'Redirect for resource {resource} not found')

    resourse_path = path.lstrip('/') if path else ''
    proxy_path = f'http://{redirect_to}/{resourse_path}'.rstrip('/')

    logger.warning('Got proxy path {} and user {!r}', proxy_path, auth_user)

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
