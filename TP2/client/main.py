from configparser import ConfigParser
import zmq
import threading
import signal
import base64
import os


def main():
    """
    This client asks the server for whatever metrics it has stored every few seconds.

    The current supported metrics are:
    - The average score of all posts
    - A sample of posts liked by students
    - The meme with the highest average sentiment
    """

    config = ConfigParser()
    config.read("./config.ini")

    server_host = (
        config["NETWORK"]["server_hostname"],
        int(config["NETWORK"]["server_port"]),
    )

    # Have a dedicated event to track if we are shutting down (on SIGTERMs) and need to
    # stop our while loop
    is_shutdown = threading.Event()
    signal.signal(signal.SIGTERM, lambda _n, _f: is_shutdown.set())

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{server_host[0]}:{server_host[1]}")

    while not is_shutdown.is_set():
        # The 'protocol' is pretty naive: just send any string and get a dict of metrics
        socket.send_string("/everything_everywhere_all_at_once")
        reply = socket.recv_json()

        if len(reply):
            print("\nGot some stuff from the server!")

        # The metrics in our dict can be plain strings or encoded ones
        # If the metric is encoded, it will provide the optional 'metric_encoded'
        # boolean in the dict
        # The encoded strings are bytes encoded into base64 and then decoded as ascii,
        # to have them as strings instead of bytestrings which can be easily sent
        # inside the dict
        for metric_name, metric in reply.items():
            if metric.get("metric_encoded"):
                # If the metric is encoded, it is intended to be saved by the client in
                # a file
                file_content = base64.b64decode(metric["metric_value"].encode("ascii"))
                filepath = f"./memes/{metric_name}.jpg"

                # We want to avoid doing fs operations if the metric didn't change
                if not os.path.exists(filepath) or os.path.getsize(filepath) != len(
                    file_content
                ):
                    with open(filepath, "wb") as f:
                        f.write(file_content)
                        print(f"* saving {metric_name} in {filepath}")

            else:
                # If the metric is not encoded, we simply print it out
                print(f"* {metric_name}: {metric['metric_value']}")

        # If the metric contains the 'metric_final' attribute, that means that the
        # server won't send us any new updates after this and we can safely shut down
        # the client
        if len(reply) and all(metric.get("metric_final") for metric in reply.values()):
            print("All metrics are final => Shutting Down")
            break

        # Ask again in a few seconds!
        # (This should probably be configurable...)
        is_shutdown.wait(10)

    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()


if __name__ == "__main__":
    main()
