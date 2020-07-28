import copy
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import cached_property
from typing import Optional, List, Dict

from pymongo.collection import Collection
from telegram import Message, ParseMode, Bot

from external.blockchain_client import BlockchainClient
from managers.db_manager import DBManager
from utils.message_utils import send_tx_info, send_tracking_info_full
from bot.settings import TTL_IN_STATUS
from utils.str_utils import timedelta_to_str, get_addr_html_url
from model.tracking import Tracking, AddressStatus, TransactionInfo


# TODO: schedule backups
@dataclass
class TrackingManager:
    blockchain_client: BlockchainClient
    db_manager: DBManager

    @cached_property
    def db(self) -> Collection:
        return self.db_manager.trackings

    @cached_property
    def trackings_by_hash(self) -> Dict[str, Tracking]:
        return {t.address: t for t in self.get_all()}

    def get_all(self) -> List[Tracking]:
        return [Tracking.from_dict(d) for d in self.db.find({})]

    def get_by_chat_id(self, chat_id: int) -> List[Tracking]:
        return [Tracking.from_dict(d) for d in self.db.find({'chat_id': chat_id})]

    def create(self, address: str, chat_id: int, status: AddressStatus, transactions: List[TransactionInfo]):
        now = datetime.now()
        new_tracking = Tracking(address, chat_id, now, status, now, transactions)
        res = self.db.insert_one(asdict(new_tracking))
        if not res.acknowledged:
            return None

        return new_tracking

    def update_tracking(self, t: Tracking) -> Tracking:
        updated = copy.deepcopy(t)
        now = datetime.now()

        # TODO: update every tx separately
        status, tx_info = self.blockchain_client.check_address(t.address)
        if status == AddressStatus.CHECK_FAILED:
            return updated

        additional_info_str = f', {tx_info.conf_cnt} confirmations' if status.has_transaction() else ''
        logging.debug(f'--> {t.address} in state {status}{additional_info_str}')

        if status != t.status:
            res = self.db.update_one({'address': t.address}, {'$set': {'status': status}})
            if res.modified_count == 0:
                logging.error(f'Failed to update status for address {t.address}')
                return updated
            updated.status = status

        if tx_info:
            for tx in updated.transactions:
                if tx.hash == tx_info.hash:
                    if tx.conf_cnt != tx_info.conf_cnt:
                        logging.debug(f'{tx.conf_cnt} -> {tx_info.conf_cnt}')
                        res = self.db.update_one(
                            {'transactions.hash': tx.hash},
                            {'$set': {'transactions.$.conf_cnt': tx.conf_cnt}}
                        )
                        if res.modified_count == 0:
                            logging.error(f'Failed to update info for tx {tx.hash}')
                            return updated
                        tx.conf_cnt = tx_info.conf_cnt

        self.db.update_one({'address': t.address}, {'$set': {'updated_at': now}})

        return updated

    def remove_tracking(self, t: Tracking) -> bool:
        res = self.db.delete_one({'address': t.address})
        if res.deleted_count > 0:
            if t.address in self.trackings_by_hash:
                del self.trackings_by_hash[t.address]
            return True
        return False

    def has_tracking_for_address(self, address: str) -> bool:
        return address in self.trackings_by_hash

    def get_tracking_by_address(self, address: str) -> Optional[Tracking]:
        return self.trackings_by_hash.get(address)

    # TODO: check maybe bot could be taken from message
    def track_address(self, address: str, message: Message, bot: Bot) -> Optional[Tracking]:
        found = self.get_tracking_by_address(address)
        if found is not None:
            # TODO: handle tx finished
            send_tracking_info_full(found, 'Чел, да я и так палю че по...')
            return found

        status, tx_info = self.blockchain_client.check_address(address)

        if status == AddressStatus.INVALID_HASH:
            message.reply_text(f'Это хуйня, а не адрес, чел)) {address} - че?)')
            return None

        if status == AddressStatus.CHECK_FAILED:
            # TODO: restart tor with status code
            message.reply_text(f'Хз че по {address}, сеш (какой-то).')
            return None

        if status == AddressStatus.CONFIRMED:
            # TODO: send how long ago
            message.reply_text('УЖЕ намошнено ЧЕЛ))')
            return None

        chat_id = message.chat.id
        new_tracking = self.create(address, chat_id, status, [tx_info])
        if status == AddressStatus.NO_TRANSACTIONS:
            bot.send_message(chat_id, f'Эх, пока ни одной транзакции на {get_addr_html_url(address)}...\n'
                                      f'Но я понаблюдаю за ним {timedelta_to_str(TTL_IN_STATUS)}, отпишу ес че',
                                      parse_mode=ParseMode.HTML)

        if status == AddressStatus.NOT_CONFIRMED:
            if tx_info.conf_cnt == 0:
                send_tx_info(new_tracking, 'Так-с, на адреске чёт пока нихуя, но я попалю хули) Базар-вокзал))')
            else:
                send_tx_info(new_tracking, 'Не ну))) Уже прям найс) Я попалю когда там че будет прям збс типа окда)')

        return new_tracking
