from fastapi import APIRouter

from app.api.v1 import auth, knowledge_graph, medical, ocr, parser, profile, recommendation, scans, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(profile.router)
api_router.include_router(scans.router)
api_router.include_router(ocr.router)
api_router.include_router(parser.router)
api_router.include_router(knowledge_graph.router)
api_router.include_router(medical.router)
api_router.include_router(recommendation.router)
