import re
from typing import List, Optional
from beanie.operators import In, Or, RegEx
from models.post import Post

async def search_posts(*,
                       language:Optional[str]=None,
                       vibe_emojis:Optional[List[str]]=None,
                       tags:Optional[List[str]]=None,
                       text:Optional[str]=None,
                       skip:int=0,
                       limit:int=10)->List[Post]:
    """
    다중 조건에 따라 게시물 검색 후 페이지네이션 적용
    """
    query = []
    
    if language:
        query.append(Post.language==language)
    
    if vibe_emojis:
        query.append(In(Post.vibeEmojis, vibe_emojis))
    
    if tags:
        query.append(In(Post.tags,tags))
    
    if text:
        query.append(
            Or(
            RegEx(Post.title, text, "i"),
            RegEx(Post.description, text, "i"),
            RegEx(Post.tags, text, "i")
        ))

    posts = await Post.find(*query).sort(-Post.createdAt).skip(skip).limit(limit).to_list()
    
    return posts