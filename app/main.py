from fastapi import FastAPI
from app.controller.auth import auth_controller
from app.controller.user import user_controller


from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Auth Service",
    description="회원가입, 로그인, 인증 기반 사용자 API",
    version="1.0.0",
    openapi_tags=[],
    swagger_ui_oauth2_redirect_url=None,
    swagger_ui_init_oauth=None
)

app.include_router(auth_controller.router)
app.include_router(user_controller.router)

@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}
