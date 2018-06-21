import requests
import json


class TranslatorBot(object):
    def __init__(self, telegram_key, ciceron_key):
        self.telegram_key = telegram_key
        self.ciceron_key  = ciceron_key

    def _translate(self, source_lang, target_lang, sentence, order_user, memo):
        endpoint = "http://translator.ciceron.me:5000/api/v2/internal/translate"
        payload = {
                    "source_lang": source_lang
                  , "target_lang": target_lang
                  , "sentence": sentence
                  , "tag": "telegram"
                  , "order_user": order_user
                  , "media": "telegram"
                  , "where_contributed": "telegram"
                  , "memo": memo
                }
        headers = {"Authorization": self.ciceron_key}
        try:
            resp = requests.post(endpoint, data=payload, headers=headers, timeout=10, verify=False)
            data = resp.json() if resp.status_code == 200 else {"ciceron":"Not enough servers. Investment is required.", 'google':""}

        except:
            data = {"ciceron":"Not enough servers. Investment is required.", 'google':""}

        result_ciceron = data.get('ciceron')
        result_google = data.get('google')
        result_human = data.get('human')
        if source_lang in ["en", "ko"] and target_lang in ["en", "ko"]:
            message  = "LangChain:\n*{}*\n\n".format(result_ciceron)
            if result_human is not None:
                message += "Human guided:\n*{}*\n\n".format(result_human)
            message += "Google:\n*{}*\n\n".format(result_google)
            message += "Powered by LangChain"

            message_usage  = "Usage: !'Source language''Target language' 'Sentence'\n"
            message_usage += "Ex) !enko Hello?\n\n"
            message_usage += "Korean - ko / English - en / Japanese - ja / Chinese - zh\nThai - th / Spanish - es / Portuguese - pt / Vietnamese - vi\nGerman - de / French - fr"
        else:
            message = "Google:\n*{}*\n\n".format(result_google)
            if result_human is not None:
                message += "Human guided:\n*{}*\n\n".format(result_human)
            message += "Powered by LangChain"

            message_usage  = "Usage: !'Source language''Target language' 'Sentence'\n"
            message_usage += "Ex) !enko Hello?\n\n"
            message_usage += "Korean - ko / English - en / Japanese - ja / Chinese - zh\nThai - th / Spanish - es / Portuguese - pt / Vietnamese - vi\nGerman - de / French - fr"

        return message, message_usage

    def _sendMessage(self, api_endpoint, chat_id, message_id, message):
        payload = {
                      "chat_id": chat_id
                    , "text": message
                    , "reply_to_message_id": message_id
                    , "parse_mode": "Markdown"
                  }

        for _ in range(100):
            resp = requests.post(api_endpoint, data=payload, timeout=5)
            if resp.status_code == 200:
                break

        else:
            print("Telegram deadlock")

        return resp.json()

    def _editMessage(self, api_endpoint, chat_id, message_id, message):
        payload = {
                      "chat_id": chat_id
                    , "text": message
                    , "message_id": message_id
                    , "parse_mode": "Markdown"
                  }

        for _ in range(100):
            resp = requests.post(api_endpoint, data=payload, timeout=5)
            if resp.status_code == 200:
                break

        else:
            print("Telegram deadlock")

        return resp.json()

    def _sendNormalMessage(self, api_endpoint, chat_id, message):
        payload = {
                      "chat_id": chat_id
                    , "text": message
                    , "parse_mode": "Markdown"
                  }

        for _ in range(100):
            resp = requests.post(api_endpoint, data=payload, timeout=5)
            if resp.status_code == 200:
                break

        else:
            print("Telegram deadlock")

    def main(self, wakeup_key
                         , chat_id, message_id, text_before, user_name
                         , chat_type=None, group_title=None):

        apiEndpoint_update = "https://api.telegram.org/bot{}/getUpdates".format(self.telegram_key)
        apiEndpoint_send = "https://api.telegram.org/bot{}/sendMessage".format(self.telegram_key)
        apiEndpoint_edit = "https://api.telegram.org/bot{}/editMessageText".format(self.telegram_key)

        if text_before.startswith(wakeup_key):
            ret = self._sendMessage(apiEndpoint_send, chat_id, message_id, "Translating...")

            new_chat_id = ret['result']['chat']['id']
            new_message_id = ret['result']['message_id']

            language_pair = text_before[:5]
            source_lang = language_pair[1:3]
            target_lang = language_pair[3:5]

            text_before = text_before.replace(language_pair, '').strip()
            print(text_before)
            message, message_usage = self._translate(source_lang, target_lang, text_before, user_name, "Telegram:{}|{}|{}".format(user_name, chat_type, group_title))
            print(message)
            self._editMessage(apiEndpoint_edit, new_chat_id, new_message_id, message)
            self._sendNormalMessage(apiEndpoint_send, chat_id, message_usage)
