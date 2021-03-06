from sqlalchemy.orm import Session


def retrieve_need_to_push_notice_device_token_list(session: Session) -> [str]:
    device_token_list = session.execute("SELECT token FROM subscription WHERE subscription.isSubscribeNotice = 1;")
    return [token[0] for token in device_token_list]
