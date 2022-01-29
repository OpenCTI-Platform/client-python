from typing import Dict

from celery import Task
from pydantic import BaseSettings


class Settings(BaseSettings):
    opencti_url: str


class StixIngester(Task):
    def __init__(self, config):
        # TODO setup
        # make everything else stateless
        self.setup(config)
        pass

    def setup(self):
        pass

    def run(
            self,
            stix_bundle: list):
    #         connection: Any,
    #         channel: BlockingChannel,
    #         delivery_tag: str,
    #         data: Dict[str, Any],
    # ) -> Optional[bool]:



        # Set the API headers
        applicant_id = data["applicant_id"]
        self.api.set_applicant_id_header(applicant_id)
        work_id = data["work_id"] if "work_id" in data else None
        # Execute the import
        self.processing_count += 1
        content = "Unparseable"
        try:
            content = base64.b64decode(data["content"]).decode("utf-8")
            types = (
                data["entities_types"]
                if "entities_types" in data and len(data["entities_types"]) > 0
                else None
            )
            update = data["update"] if "update" in data else False
            processing_count = self.processing_count
            if self.processing_count == PROCESSING_COUNT:
                processing_count = None  # type: ignore
            self.api.stix2.import_bundle_from_json(
                content, update, types, processing_count
            )
            # Ack the message
            cb = functools.partial(self.ack_message, channel, delivery_tag)
            connection.add_callback_threadsafe(cb)
            if work_id is not None:
                self.api.work.report_expectation(work_id, None)
            self.processing_count = 0
            return True
        except Timeout as te:
            logging.warning("%s", f"A connection timeout occurred: {{ {te} }}")
            # Platform is under heavy load: wait for unlock & retry almost indefinitely.
            sleep_jitter = round(random.uniform(10, 30), 2)
            time.sleep(sleep_jitter)
            self.data_handler(connection, channel, delivery_tag, data)
            return True
        except RequestException as re:
            logging.error("%s", f"A connection error occurred: {{ {re} }}")
            time.sleep(60)
            logging.info(
                "%s", f"Message (delivery_tag={delivery_tag}) NOT acknowledged"
            )
            cb = functools.partial(self.nack_message, channel, delivery_tag)
            connection.add_callback_threadsafe(cb)
            self.processing_count = 0
            return False
        except Exception as ex:  # pylint: disable=broad-except
            error = str(ex)
            if "LockError" in error and self.processing_count < MAX_PROCESSING_COUNT:
                # Platform is under heavy load:
                # wait for unlock & retry almost indefinitely.
                sleep_jitter = round(random.uniform(10, 30), 2)
                time.sleep(sleep_jitter)
                self.data_handler(connection, channel, delivery_tag, data)
            elif (
                    "MissingReferenceError" in error
                    and self.processing_count < PROCESSING_COUNT
            ):
                # In case of missing reference, wait & retry
                sleep_jitter = round(random.uniform(1, 3), 2)
                time.sleep(sleep_jitter)
                logging.info(
                    "%s",
                    (
                        f"Message (delivery_tag={delivery_tag}) "
                        f"reprocess (retry nb: {self.processing_count})"
                    ),
                )
                self.data_handler(connection, channel, delivery_tag, data)
            else:
                # Platform does not know what to do and raises an error:
                # fail and acknowledge the message.
                logging.error(error)
                self.processing_count = 0
                cb = functools.partial(self.ack_message, channel, delivery_tag)
                connection.add_callback_threadsafe(cb)
                if work_id is not None:
                    self.api.work.report_expectation(
                        work_id, {"error": error, "source": content}
                    )
                return False
            return None
