"""
This file is personal recommendation system based contents for meta data to vectorization.
"""
import asyncio
import os, sys, uuid
import numpy as np
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import AsyncSessionLocal, engine
from db.mongodb import init_db, close_connection
from models.post import Post
from models.post_vector import PostVector, VECTOR_DIMENSION

async def vectorize_post(post:Post, model:SentenceTransformer)->np.ndarray:
    """
    게시물 하나를 의미 벡터로 변환
    title, tags, language -> 텍스트 결합
    """
    text_to_embed = f"Title:{post.title}\nLanuage:{post.language}\nTags:{','.join(post.tags)}\n\n{post.description}"
    vector = model.encode(text_to_embed)
    return vector

async def run_vectorization(model:SentenceTransformer):
    """
    MongoDB Post -> pgvector 동기화 
    """
    print("Start vectorization...")
    async with AsyncSessionLocal() as session:
        try:
            # STEP 1. 이미 벡터화된 post_id 목록 가져오기 -> 효율적 처리
            query = await session.execute(select(PostVector.post_id))
            exsiting_post_ids = set(query.scalars().all())
            
            # STEP 2. MongoDB에서 아직 벡터화되지 않은 새 게시물 찾기
            new_posts = await Post.find({"_id" : {"$nin":list(exsiting_post_ids)}}
                                        ).to_list()
            if not new_posts:
                print("Not exsits new post for vectorization")
                return
            print(f"{len(new_posts)} new posts found..Starting vectorization..")
            
            vectors_to_insert = []
            for post in new_posts:
                vector = await vectorize_post(post=post, model=model)
                if vector.shape[0] != VECTOR_DIMENSION:
                    print(f"Warning: Vector dimension of {post.id} is {vector.shape[0]} which is different from {VECTOR_DIMENSION}.")
                    continue
                
                vectors_to_insert.append({
                    "id" : uuid.uuid4(),
                    "post_id" : str(post.id),
                    "language" : str(post.language),
                    "vector" : vector.tolist()
                })
                
            if not vectors_to_insert:
                print("No valid vector to insert")
                return
            
            # STEP 3. PostgreSQL에 일괄 삽입 -> post_id가 존재(충돌)하면 아무것도 하지 않음
            stmt = insert(PostVector).values(vectors_to_insert)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['post_id']
            )
            
            await session.execute(stmt)
            await session.commit()
            
            print(f"Successfully saved {len(vectors_to_insert)} new post vectors")
        except Exception as e:
            print(f"Error occured while vectorizing: {e}")
        
if __name__ == "__main__":
    async def main():
        # 'all-MiniLM-L6-V2' -> 384 차원 벡터 생성 경량 모델
        try:
            model = SentenceTransformer('all-MiniLM-L6-V2')
            print('Model loaded successfully..')
        except Exception as e:
            print(f"Failed model load..{e}")
            sys.exit(1)
            
        await init_db()
        await run_vectorization(model=model)
        
        if engine:
            await engine.dispose()
        await close_connection()
        
        del model
        
    asyncio.run(main())