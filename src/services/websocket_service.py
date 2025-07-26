import json
import asyncio
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from src.services.ai_service import AIService
from src.models.ai_models import AIRequest, AITaskType, AIProvider
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Set[str]] = {}
        self.ai_service = None  # Initialize lazily

    def _get_ai_service(self):
        """Lazy initialization of AI service"""
        if self.ai_service is None:
            self.ai_service = AIService()
        return self.ai_service

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[session_id] = websocket

        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)

        logger.info(f"WebSocket connected: session={session_id}, user={user_id}")

        # Send welcome message
        await self.send_message(session_id, {
            "type": "connection_established",
            "session_id": session_id,
            "message": "Connected to Cursor Clone AI Service"
        })

    def disconnect(self, session_id: str, user_id: str):
        """Disconnect a WebSocket client"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]

        logger.info(f"WebSocket disconnected: session={session_id}, user={user_id}")

    async def send_message(self, session_id: str, message: dict):
        """Send message to specific session"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to session {session_id}: {str(e)}")
                # Remove broken connection
                if session_id in self.active_connections:
                    del self.active_connections[session_id]

    async def broadcast_to_user(self, user_id: str, message: dict):
        """Broadcast message to all sessions of a user"""
        if user_id in self.user_sessions:
            tasks = []
            for session_id in self.user_sessions[user_id].copy():  # Use copy to avoid modification during iteration
                tasks.append(self.send_message(session_id, message))

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def handle_ai_request(self, session_id: str, user_id: str,data: dict):
        """Handle AI request through WebSocket"""
        try:
            # Parse request
            ai_request = AIRequest(
                task_type=AITaskType(data.get("task_type", "chat")),
                provider=AIProvider(data.get("provider", "gemini")),
                prompt=data.get("prompt", ""),
                context=data.get("context"),
                language=data.get("language"),
                model_params=data.get("model_params", {}),
                user_id=user_id,
                session_id=session_id
            )

            # Send acknowledgment
            await self.send_message(session_id, {
                "type": "ai_request_received",
                "request_id": session_id,
                "status": "processing",
                "task_type": ai_request.task_type.value
            })

            # Process request
            ai_service = self._get_ai_service()
            response = await ai_service.process_request(ai_request)

            # Send response
            await self.send_message(session_id, {
                "type": "ai_response",
                "request_id": session_id,
                "task_type": ai_request.task_type.value,
                "success": response.success,
                "response": response.response,
                "metadata": response.metadata,
                "processing_time": response.processing_time,
                "error_message": response.error_message
            })

        except Exception as e:
            logger.error(f"WebSocket AI request error: {str(e)}")
            await self.send_message(session_id, {
                "type": "error",
                "message": f"AI request failed: {str(e)}"
            })

    async def handle_message(self, session_id: str, user_id: str, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "ai_request":
                await self.handle_ai_request(session_id, user_id, data)
            elif message_type == "ping":
                await self.send_message(session_id, {"type": "pong"})
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send_message(session_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message from session {session_id}: {e}")
            await self.send_message(session_id, {
                "type": "error",
                "message": "Invalid JSON format"
            })
        except Exception as e:
            logger.error(f"Message handling error: {str(e)}")
            await self.send_message(session_id, {
                "type": "error",
                "message": str(e)
            })


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
