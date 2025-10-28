from sqlalchemy import Column, String, Index
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from db.database import Base
import uuid

VECTOR_DIMENSION=384

class PostVector(Base):
    __tablename__ = "post_vectors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(String, unique=True, nullable=False, index=True)
    language = Column(String, index=True)
    vector = Column(Vector(VECTOR_DIMENSION), nullable=True)
    
    __table_args__ = (
        Index(
            'ix_post_vectors_vector',
            vector,
            postgresql_using = 'ivfflat',
            postgresql_with={'lists':100},
            postgresql_ops={'vector' : 'vector_cosine_ops'} 
        ),
    )