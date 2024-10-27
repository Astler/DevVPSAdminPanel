from typing import Dict
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class ShardManager:
    _instances: Dict[int, 'ShardManager'] = {}
    _shard_map = {
        # project_id: shard_number
    }

    def __init__(self, shard_number: int):
        self.shard_number = shard_number
        self.engine = create_engine(f'sqlite:///instance/analytics_shard_{shard_number}.db')
        self.Session = sessionmaker(bind=self.engine)

    @classmethod
    def get_shard_for_project(cls, project_id: int) -> 'ShardManager':
        shard_number = cls._shard_map.get(project_id)
        if not shard_number:
            # Simple sharding strategy - can be made more sophisticated
            shard_number = project_id % 10  # 10 shards
            cls._shard_map[project_id] = shard_number

        if shard_number not in cls._instances:
            cls._instances[shard_number] = ShardManager(shard_number)

        return cls._instances[shard_number]

    def get_session(self):
        return self.Session()