from fast_bitrix24 import BitrixAsync

from ..Configs.config import settings
from ..Logs.logging_setup import app_logger as logger

from ..BD.users_db import distribute_tasks, get_available_users
from ..Utils.BitrixErrors import ServerBitrixErrors as errorBitrix


async def process_company_random(task, b: BitrixAsync):
    deal_id = task['deal_id']
    cont_id = task['cont_id']
    # Проверка на наличие параметров
    if deal_id is None or cont_id is None:
        logger.error('deal_id = None or cont_id = None', extra={'task': task})
        return False
    # Проверка, что за контакт уже ответственный другой человек,
    # значит он должен быть ответственным за сделку
    try:
        as_id = await get_contact_assigned_id(cont_id, b)
        # Если ответсвенный за контакт не пустой и != акк. Технической поддержки
        if as_id and as_id != settings.TECH_ACCOUNT:
            await assign_deal(deal_id, as_id, b)
            logger.info(f'Integration with Bitrix24 is Done,'
                        f'old_as_id: {as_id}', extra={'task': task})
            return True
    except errorBitrix as e:
        logger.error(f'Error in Bitrix: {e}', extra={'task': task})
        return False
    except Exception as e:
        logger.error(f'Error: {e}', extra={'task': task})
        return False

    # Если ответственный = мы, делаем распределение и переназначаем сущности
    try:
        random_guy, random_name = await distribute_tasks()
        av_users = await get_available_users()
        logger.info(f'New random guy was chosen: id={random_guy}, name={random_name}, av_users={av_users}')
        await assign_entities(deal_id, cont_id, random_guy, b)
        logger.info(f'Integration with Bitrix24 is Done,'
                    f'new_as_id: {random_guy}, new_name={random_name},',
                    extra={'task': task})
        return True
    except Exception as e:
        logger.error(f'Error: {e}')
        return False


async def get_contact_assigned_id(cont_id: str, b: BitrixAsync) -> str | None:
    contact = await b.get_by_ID("crm.contact.get", [cont_id])
    return contact.get("ASSIGNED_BY_ID", None)


async def assign_entities(deal_id: str, cont_id: str, assigned_id: str, b: BitrixAsync) -> None:
    deal = await b.call('crm.deal.update', {'id': deal_id, 'fields': {'ASSIGNED_BY_ID': assigned_id}})
    contact = await b.call('crm.contact.update', {'id': cont_id, 'fields': {'ASSIGNED_BY_ID': assigned_id}})
    if not deal:
        raise errorBitrix(f"Deal wasn't updated in Bitrix24, deal_id: {deal_id}")
    if not contact:
        raise errorBitrix(f"Contact wasn't updated in Bitrix24, cont_id: {cont_id}")


async def assign_deal(deal_id: str, assigned_id: str, b: BitrixAsync) -> None:
    deal = await b.call('crm.deal.update', {'id': deal_id, 'fields': {'ASSIGNED_BY_ID': assigned_id}})
    if not deal:
        raise errorBitrix(f"Deal wasn't updated in Bitrix24, deal_id: {deal_id}")
