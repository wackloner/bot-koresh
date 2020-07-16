from dataclasses import dataclass, asdict
from functools import cached_property
from typing import Optional

from managers.db_manager import DBManager
from model.user import User, FileInfo


@dataclass
class UserManager:
    db_manager: DBManager

    @cached_property
    def users(self):
        return self.db_manager.users

    def create(self, user_id: int, user_name: str, msg_cnt: int = 0) -> User:
        new_user = User(user_id, user_name, msg_cnt)
        new_user_dict = self.users.insert_one(asdict(new_user))
        return User.from_dict(new_user_dict)

    def get(self, user_id: int) -> Optional[User]:
        user_dict = self.users.find_one({'id': user_id})
        return User.from_dict_o(user_dict)

    def get_or_create(self, user_id: int, user_name: str, msg_cnt: int = 0) -> User:
        user = self.get(user_id=user_id)
        return user if user is not None else self.create(user_id, user_name, msg_cnt)

    def update_user_with_new_file(self, user: User, file_info: FileInfo) -> Optional[User]:
        user.stored_files.append(file_info)
        user_dict = self.users.update_one({'id': user.id}, {'$set': {'stored_files': user.stored_files}})
        return User.from_dict_o(user_dict)
