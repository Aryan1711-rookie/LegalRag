
from fastapi import APIRouter, Request, HTTPException, Depends

from api.schema.chat import ChatRequest, ChatResponse
from api.dependencies.auth import get_current_user

from database.document_repository import DocumentRepository
from database.chat_repository import ChatRepository

from api.schema.chat import ChatSaveRequest
from database.chat_repository import ChatRepository

router = APIRouter(
    prefix="/api/v1",
    tags=["Chat"]
)


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    request: Request,
    user=Depends(get_current_user)
):
    try:
        user_id = str(user.id)
        document_id = str(payload.document_id)

        # 1. Verify document ownership.
        document_repository = DocumentRepository()

        document = document_repository.get_document_for_user(
            document_id=document_id,
            user_id=user_id
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found."
            )

        chat_repository = ChatRepository()

        # 2. Create a new chat or verify an existing chat.
        if payload.chat_id:
            chat_id = str(payload.chat_id)

            existing_chat = chat_repository.get_chat_for_user(
                chat_id=chat_id,
                user_id=user_id
            )

            if not existing_chat:
                raise HTTPException(
                    status_code=404,
                    detail="Chat not found."
                )

            # Prevent switching the document inside an existing chat.
            if existing_chat.get("document_id") != document_id:
                raise HTTPException(
                    status_code=400,
                    detail="This chat belongs to a different document."
                )

        else:
            new_chat = chat_repository.create_chat(
                user_id=user_id,
                title=payload.question[:60],
                document_id=document_id
            )

            if not new_chat:
                raise HTTPException(
                    status_code=500,
                    detail="Unable to create chat."
                )

            chat_id = new_chat["id"]

        # 3. Save the user's message.
        user_message = chat_repository.add_message_for_user(
            chat_id=chat_id,
            user_id=user_id,
            role="user",
            content=payload.question
        )

        if not user_message:
            raise HTTPException(
                status_code=500,
                detail="Unable to save your message."
            )

        # 4. Execute the existing RAG pipeline.
        rag_service = request.app.state.rag_service

        result = rag_service.answer_question(
            payload.question,
            document_id=document_id
        )

        # 5. Save the assistant's response.
        assistant_message = chat_repository.add_message_for_user(
            chat_id=chat_id,
            user_id=user_id,
            role="assistant",
            content=result["answer"]
        )

        if not assistant_message:
            raise HTTPException(
                status_code=500,
                detail="Unable to save the assistant response."
            )

        # 6. Return the conversation ID with the RAG response.
        return {
            **result,
            "chat_id": chat_id
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error occurred while processing the question: {e}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the question."
        )


@router.get("/chats/saved")
def get_saved_chats(user=Depends(get_current_user)):
    try:
        chat_repository = ChatRepository()

        chats = chat_repository.get_saved_chats_for_user(
            user_id=str(user.id)
        )

        return {
            "chats": chats,
            "total": len(chats)
        }

    except Exception as e:
        print(f"Saved chats retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve saved chats"
        )


@router.patch("/chats/{chat_id}/saved")
def update_chat_saved_status(
    chat_id: str,
    payload: ChatSaveRequest,
    user=Depends(get_current_user)
):
    try:
        chat_repository = ChatRepository()

        chat = chat_repository.update_chat_saved_status(
            chat_id=chat_id,
            user_id=str(user.id),
            is_saved=payload.is_saved
        )

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )

        return {
            "id": chat["id"],
            "title": chat["title"],
            "is_saved": chat["is_saved"]
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Chat save update error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update chat saved status"
        )

@router.get("/chats/{chat_id}/messages")
def get_chat_messages(
    chat_id: str,
    user=Depends(get_current_user)
):
    try:
        chat_repository = ChatRepository()
        user_id = str(user.id)

        # Verify chat ownership
        chat = chat_repository.get_chat_for_user(
            chat_id=chat_id,
            user_id=user_id
        )

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )

        messages = chat_repository.get_messages_for_chat(
            chat_id=chat_id,
            user_id=user_id
        )

        return {
            "chat": chat,
            "messages": messages or []
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Chat history retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve chat history"
        )
