from typing import List
from models.user import User
from models.post import Post
from schema.post import PostCreate

async def create_new_post(post_data:PostCreate,
                          user:User,
                          vibe_emojis:List[str])->Post:
    """
    
    """
    new_post = Post(
        **post_data.model_dump(),
        authorId=user.id,
        authorNickname=user.nickname,
        authorProfileImage=user.profile_image_url,
        vibeEmojis=vibe_emojis
    )
    await new_post.create()
    
    return new_post