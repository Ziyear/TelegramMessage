import os
import pickle

import config


def resend_message(id):
  os.system(
      f"cp {config.data['session_name']}.session {config.data['session_name']}_new.session")
  client = config.get_client()
  client.start()

  sender = config.get_sender(id)
  if not sender:
    return False
  try:
    sender = pickle.loads(sender)
    client.send_message(sender, config.data['message'])
    config.update_message(id, 'success')
    return True
  except Exception as e:
    config.logging.error("resend message error")
    config.logging.exception(e)
    config.update_message(id, 'error')
  finally:
    client.disconnect()
    os.system(f"rm -f {config.data['session_name']}_new.session")
