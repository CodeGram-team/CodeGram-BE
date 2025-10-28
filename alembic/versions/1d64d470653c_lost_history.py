"""
이 파일은 코드가 유실되어 비어있는, 
데이터베이스에 이미 적용된 첫 번째 마이그레이션입니다.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d64d470653c' # <-- 에러에 나온 그 ID를 여기에 적습니다.
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 데이터베이스에는 이미 이 테이블들이 존재하므로,
    # 여기서는 아무 작업도 하지 않도록 'pass'를 사용합니다.
    pass


def downgrade() -> None:
    # 되돌릴 수 없으므로 'pass'를 사용합니다.
    pass