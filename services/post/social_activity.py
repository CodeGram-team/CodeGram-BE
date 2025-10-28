from uuid import UUID
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from models.post import Like,Post, Comment
from models.user import User
from schema.post import CommentCreate

async def toggle_like(post_id:PydanticObjectId, user_id:UUID):
    """
    특정 게시물에 대한 사용자 좋아요 상태 토클
    STEP 
    1. likes 컬렉션에서 좋아요 기록 찾음
    2. 기록이 있으면 좋아요 취소 (like 삭제, post.likesCount 1 감소)
    3. 기록이 없으면 좋아요 추가 (like 생성, post.likesCount 1 증가)
    """
    existing_like = await Like.find_one(
        Like.userId == user_id,
        Like.postId == post_id
    )
    if existing_like:
        await existing_like.delete()
        
        updated_post = await Post.find_one(
            Post.id == post_id
        ).update(
            {"$inc": {Post.likesCount: -1}},
            response_type="update_and_return"
        )
        user_liked = False
    else:
        try:
            like = Like(userId=user_id, postId=post_id)
            await like.insert()
            
            updated_post = await Post.find_one(
                Post.id == post_id
            ).update(
                {"$inc" : {Post.likesCount: 1}},
                response_type="update_and_return"
            )
            user_liked = True
        except DuplicateKeyError:
            updated_post = await Post.get(post_id)
            user_liked = True
    
    return updated_post, user_liked

async def leave_comment(comment:CommentCreate,
                        post_id:PydanticObjectId,
                        current_user:User)->Post:
    """
    특정 게시글 사용자 댓글 추가 
    """
    new_comment = Comment(
        authorId=current_user.id,
        authorNickname=current_user.nickname,
        content=comment.content
    )
    
    await Post.find_one(Post.id==post_id).update(
        {"$push" : {"comments" : new_comment.model_dump(by_alias=True)}}
    )
    updated_post = await Post.find_one(Post.id==post_id)
    
    if not updated_post:
        return None
    
    return updated_post